"""
Agent 3: Navigator Agent
Responsible for navigating career pages using Selenium.
"""
import json
import time
from typing import Optional, List, Dict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .base_agent import BaseAgent, AgentContext, AgentMessage, AgentStatus

# JavaScript snippet injected before page scripts to monitor XHR/fetch activity.
_NETWORK_MONITOR_JS = """
window.__pendingRequests = 0;
window.__completedRequests = [];
window.__lastRequestTime = Date.now();

// Patch XMLHttpRequest
const origOpen = XMLHttpRequest.prototype.open;
const origSend = XMLHttpRequest.prototype.send;
XMLHttpRequest.prototype.open = function(method, url) {
    this._url = url;
    this._method = method;
    return origOpen.apply(this, arguments);
};
XMLHttpRequest.prototype.send = function() {
    window.__pendingRequests++;
    window.__lastRequestTime = Date.now();
    this.addEventListener('loadend', function() {
        window.__pendingRequests--;
        window.__lastRequestTime = Date.now();
        if (this._url) {
            try {
                window.__completedRequests.push({
                    url: this._url,
                    method: this._method || 'GET',
                    status: this.status,
                    type: 'xhr',
                    contentType: this.getResponseHeader('content-type') || '',
                    bodySnippet: (this.responseText || '').substring(0, 500)
                });
            } catch(e) {}
        }
    });
    return origSend.apply(this, arguments);
};

// Patch fetch
const origFetch = window.fetch;
window.fetch = function(input, opts) {
    window.__pendingRequests++;
    window.__lastRequestTime = Date.now();
    const urlStr = typeof input === 'string' ? input : (input && input.url) || '';
    const method = (opts && opts.method) || 'GET';
    return origFetch.apply(this, arguments).then(resp => {
        window.__pendingRequests--;
        window.__lastRequestTime = Date.now();
        const ct = resp.headers.get('content-type') || '';
        // Clone and read body for JSON API responses
        if (ct.includes('json')) {
            resp.clone().text().then(body => {
                window.__completedRequests.push({
                    url: urlStr, method: method, status: resp.status,
                    type: 'fetch', contentType: ct,
                    bodySnippet: body.substring(0, 2000)
                });
            }).catch(() => {});
        } else {
            window.__completedRequests.push({
                url: urlStr, method: method, status: resp.status,
                type: 'fetch', contentType: ct, bodySnippet: ''
            });
        }
        return resp;
    }).catch(err => {
        window.__pendingRequests--;
        window.__lastRequestTime = Date.now();
        throw err;
    });
};
"""

# CSS selector for elements that indicate job content has rendered
_JOB_CONTENT_SELECTOR = (
    '[class*="job" i], [class*="position" i], [class*="opening" i], '
    '[class*="career" i], [class*="vacancy" i], [class*="posting" i], '
    '[data-job-id], [data-automation-id="jobTitle"], '
    'a[href*="/job"], a[href*="/position"], a[href*="/career"]'
)


class NavigatorAgent(BaseAgent):
    """
    Navigates career pages using Selenium WebDriver.

    Executes navigation plans created by PageAnalyzerAgent:
    - Handles JavaScript-heavy pages with smart content waiting
    - Intercepts XHR/fetch API calls for SPA career pages
    - Clicks "Load More" buttons
    - Navigates numbered pagination
    - Handles infinite scroll
    - Expands accordions/sections
    """

    def __init__(self, llm=None, headless: bool = True):
        super().__init__("NavigatorAgent", llm)
        self.headless = headless
        self.driver: Optional[webdriver.Chrome] = None
        self._network_capture_enabled = False

    def execute(self, context: AgentContext, message: AgentMessage) -> AgentMessage:
        """Execute the navigation plan."""
        self.status = AgentStatus.RUNNING

        career_url = context.career_url
        nav_plan = context.navigation_plan

        if not career_url:
            return self._create_response(
                "orchestrator",
                "navigation_failed",
                {},
                AgentStatus.FAILED,
                "No career URL provided"
            )

        self.log(f"Navigating: {career_url}")
        self.log(f"Strategy: {nav_plan.get('pagination_strategy', 'unknown')}")

        try:
            # Initialize browser
            self._init_browser()

            # Inject network monitor BEFORE loading the page so we capture
            # all XHR/fetch requests from the very first script execution.
            self._inject_network_monitor()

            # Load the page
            self.driver.get(career_url)
            time.sleep(2)  # Brief initial settle

            # Execute navigation steps
            all_html_pages = []
            for step in nav_plan.get("steps", []):
                action = step.get("action")
                self.log(f"Executing: {action}")

                if action == "wait_for_js":
                    self._wait_for_js(step.get("timeout", 15000))

                elif action == "scroll_to_bottom":
                    self._scroll_to_bottom(step.get("wait_after", 2000))

                elif action == "click_load_more":
                    pages_html = self._click_load_more(
                        step.get("selector"),
                        step.get("button_text", []),
                        step.get("max_clicks", 10),
                        known_urls=context.known_job_urls,
                    )
                    all_html_pages.extend(pages_html)

                elif action == "navigate_pages":
                    pages_html = self._navigate_numbered_pages(
                        step.get("max_pages", 30),
                        known_urls=context.known_job_urls,
                    )
                    all_html_pages.extend(pages_html)

                elif action == "infinite_scroll":
                    self._infinite_scroll(
                        step.get("max_scrolls", 20),
                        step.get("wait_between", 2000),
                        known_urls=context.known_job_urls,
                    )

                elif action == "expand_sections":
                    self._expand_sections()

            # Get final page HTML
            final_html = self.driver.page_source
            if final_html not in all_html_pages:
                all_html_pages.append(final_html)

            # Update context with all collected HTML
            context.page_html = final_html  # Keep final state

            # Capture any intercepted API data
            context.intercepted_api_data = self.get_intercepted_api_responses()
            if context.intercepted_api_data:
                self.log(f"Captured {len(context.intercepted_api_data)} API responses")

            self.log(f"Navigation complete. Collected {len(all_html_pages)} page states")

            return self._create_response(
                "orchestrator",
                "navigation_complete",
                {
                    "pages_collected": len(all_html_pages),
                    "all_html": all_html_pages,
                    "final_url": self.driver.current_url
                },
                AgentStatus.SUCCESS
            )

        except Exception as e:
            self.log(f"Navigation error: {e}")
            return self._create_response(
                "orchestrator",
                "navigation_failed",
                {"error": str(e)},
                AgentStatus.FAILED,
                str(e)
            )

    # ------------------------------------------------------------------
    # Browser initialisation
    # ------------------------------------------------------------------

    def _init_browser(self, enable_network_capture: bool = False):
        """Initialize Selenium WebDriver."""
        if self.driver:
            return

        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )

        if enable_network_capture:
            chrome_options.set_capability(
                'goog:loggingPrefs', {'performance': 'ALL'}
            )
            self._network_capture_enabled = True

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)

    def reinit_with_network_capture(self):
        """Close and reinitialize browser with CDP network capture enabled."""
        self.close()
        self._init_browser(enable_network_capture=True)

    # ------------------------------------------------------------------
    # Smart content waiting (replaces naive document.readyState check)
    # ------------------------------------------------------------------

    def _wait_for_js(self, timeout_ms: int):
        """Backward-compatible wrapper around _wait_for_content."""
        self._wait_for_content(timeout_ms)

    def _wait_for_content(self, timeout_ms: int = 15000):
        """
        Progressive content waiting — three tiers of checks.

        Tier 1 (fast):  document.readyState + meaningful visible text
        Tier 2 (medium): job-like DOM elements appear
        Tier 3 (slow):  network idle (no pending XHR/fetch for 2 s)
        """
        start = time.time()

        # --- Tier 1: readyState + visible text check (up to 5 s) --------
        tier1_timeout = min(5, timeout_ms / 1000)
        try:
            WebDriverWait(self.driver, tier1_timeout).until(
                lambda d: d.execute_script(
                    "return document.readyState") == "complete"
            )
        except TimeoutException:
            pass

        # Quick check: does the body already contain substantial content?
        text_len = self.driver.execute_script(
            "var el = document.body.cloneNode(true);"
            "el.querySelectorAll('script,style,noscript').forEach(s => s.remove());"
            "return el.innerText.length;"
        )
        link_count = self.driver.execute_script(
            "return document.querySelectorAll('a').length;"
        )
        if text_len > 500 and link_count > 5:
            elapsed = int((time.time() - start) * 1000)
            self.log(f"Content ready (Tier 1, {elapsed}ms): {text_len} chars, {link_count} links")
            return

        # --- Tier 2: wait for job-like DOM elements (up to 10 s) ---------
        remaining = max(1, (timeout_ms / 1000) - (time.time() - start))
        tier2_timeout = min(10, remaining)
        try:
            WebDriverWait(self.driver, tier2_timeout).until(
                lambda d: d.execute_script(
                    f"return document.querySelectorAll(\"{_JOB_CONTENT_SELECTOR}\").length"
                ) >= 3
            )
            elapsed = int((time.time() - start) * 1000)
            job_els = self.driver.execute_script(
                f"return document.querySelectorAll(\"{_JOB_CONTENT_SELECTOR}\").length"
            )
            self.log(f"Content ready (Tier 2, {elapsed}ms): {job_els} job elements found")
            return
        except TimeoutException:
            pass

        # --- Tier 3: network idle for 2 seconds (remaining budget) -------
        remaining = max(1, (timeout_ms / 1000) - (time.time() - start))
        deadline = time.time() + remaining
        idle_start = None
        idle_threshold = 2.0  # seconds with 0 pending requests

        while time.time() < deadline:
            if self._is_network_idle():
                if idle_start is None:
                    idle_start = time.time()
                elif time.time() - idle_start >= idle_threshold:
                    elapsed = int((time.time() - start) * 1000)
                    self.log(f"Content ready (Tier 3 network idle, {elapsed}ms)")
                    return
            else:
                idle_start = None
            time.sleep(0.3)

        elapsed = int((time.time() - start) * 1000)
        self.log(f"Content wait exhausted ({elapsed}ms), proceeding anyway")

    # ------------------------------------------------------------------
    # Network monitoring helpers
    # ------------------------------------------------------------------

    def _inject_network_monitor(self):
        """Inject JS to track pending XHR/fetch requests.

        Uses CDP Page.addScriptToEvaluateOnNewDocument so the monitor
        runs before any page scripts, capturing every request.
        """
        if not self.driver:
            return
        try:
            self.driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {"source": _NETWORK_MONITOR_JS}
            )
        except Exception as e:
            # Fallback: inject directly (may miss early requests)
            self.log(f"CDP inject failed ({e}), using direct injection")
            try:
                self.driver.execute_script(_NETWORK_MONITOR_JS)
            except Exception:
                pass

    def _is_network_idle(self) -> bool:
        """Return True when no XHR/fetch requests are in flight."""
        if not self.driver:
            return True
        try:
            pending = self.driver.execute_script(
                "return window.__pendingRequests || 0"
            )
            return pending == 0
        except Exception:
            return True

    def get_intercepted_api_responses(self) -> list:
        """Return completed XHR/fetch requests that look like job-data APIs.

        Filters for JSON responses whose URL contains job-related keywords.
        """
        if not self.driver:
            return []

        api_keywords = [
            'api', 'job', 'position', 'career', 'search', 'graphql',
            'query', 'listing', 'opening', 'requisition', 'posting',
            'vacancy', 'result', 'talent',
        ]

        results = []
        try:
            completed = self.driver.execute_script(
                "return window.__completedRequests || []"
            )
            for req in completed:
                url = (req.get('url') or '').lower()
                ct = (req.get('contentType') or '').lower()
                body = req.get('bodySnippet') or ''

                # Only keep JSON responses with job-related URLs
                if 'json' in ct and any(kw in url for kw in api_keywords):
                    results.append({
                        'url': req.get('url', ''),
                        'method': req.get('method', ''),
                        'status': req.get('status', 0),
                        'body': body,
                    })
        except Exception:
            pass

        # Also pull from CDP performance logs if enabled
        results.extend(self._get_api_responses_from_logs())

        return results

    def _get_api_responses_from_logs(self) -> list:
        """Extract JSON API responses from Chrome performance logs (CDP)."""
        if not self._network_capture_enabled or not self.driver:
            return []

        api_keywords = [
            'api', 'job', 'position', 'career', 'search', 'graphql',
            'query', 'listing', 'opening', 'requisition',
        ]
        results = []

        try:
            logs = self.driver.get_log('performance')
            for entry in logs:
                try:
                    log_data = json.loads(entry['message'])
                    msg = log_data.get('message', {})

                    if msg.get('method') != 'Network.responseReceived':
                        continue

                    params = msg.get('params', {})
                    response = params.get('response', {})
                    url = response.get('url', '')
                    mime = response.get('mimeType', '')

                    if 'json' not in mime:
                        continue
                    if not any(kw in url.lower() for kw in api_keywords):
                        continue

                    request_id = params.get('requestId')
                    body = ''
                    try:
                        resp = self.driver.execute_cdp_cmd(
                            'Network.getResponseBody',
                            {'requestId': request_id}
                        )
                        body = (resp.get('body') or '')[:2000]
                    except Exception:
                        pass

                    results.append({
                        'url': url,
                        'method': '',
                        'status': response.get('status', 0),
                        'body': body,
                    })
                except Exception:
                    continue
        except Exception:
            pass

        return results

    # ------------------------------------------------------------------
    # Pagination / scroll helpers (unchanged)
    # ------------------------------------------------------------------

    def _scroll_to_bottom(self, wait_after_ms: int):
        """Scroll to the bottom of the page."""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(wait_after_ms / 1000)

    def _click_load_more(
        self,
        selector: Optional[str],
        button_texts: List[str],
        max_clicks: int,
        known_urls: set = None,
    ) -> List[str]:
        """Click 'Load More' button repeatedly."""
        pages_html = []
        clicks = 0

        for _ in range(max_clicks):
            # Early exit if most jobs on page are already known
            if known_urls and clicks > 0 and self._should_stop_pagination(known_urls):
                break

            # Save current state
            pages_html.append(self.driver.page_source)

            # Scroll to bottom first
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

            # Try to find and click load more button
            clicked = False

            # Try by selector first
            if selector:
                try:
                    btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    self.driver.execute_script("arguments[0].click();", btn)
                    clicked = True
                    clicks += 1
                    self.log(f"Clicked load more (page {clicks + 1})")
                    time.sleep(2)
                except Exception:
                    pass

            # Try by button text
            if not clicked:
                try:
                    buttons = self.driver.find_elements(By.TAG_NAME, 'button')
                    for btn in buttons:
                        btn_text = btn.text.strip().upper()
                        if btn_text in ['LOAD MORE', 'SHOW MORE', 'VIEW MORE', 'MORE JOBS']:
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                            time.sleep(0.5)
                            self.driver.execute_script("arguments[0].click();", btn)
                            clicked = True
                            clicks += 1
                            self.log(f"Clicked '{btn_text}' (page {clicks + 1})")
                            time.sleep(2)
                            break
                except Exception:
                    pass

            if not clicked:
                self.log(f"No more 'Load More' buttons found after {clicks} clicks")
                break

        return pages_html

    def _navigate_numbered_pages(self, max_pages: int, known_urls: set = None) -> List[str]:
        """Navigate through numbered pagination."""
        pages_html = []
        current_page = 1

        for page_num in range(1, max_pages + 1):
            # Early exit if most jobs on page are already known
            if known_urls and page_num > 1 and self._should_stop_pagination(known_urls):
                break

            # Collect current page HTML
            pages_html.append(self.driver.page_source)

            if page_num >= max_pages:
                break

            # Try to navigate to next page
            next_page = page_num + 1
            navigated = False

            # Try clicking the page number
            try:
                page_links = self.driver.find_elements(
                    By.XPATH,
                    f'//a[text()="{next_page}"] | //button[text()="{next_page}"]'
                )
                if page_links:
                    self.driver.execute_script("arguments[0].click();", page_links[0])
                    navigated = True
                    self.log(f"Navigated to page {next_page}")
                    time.sleep(2)
            except Exception:
                pass

            # Try clicking ">" or "Next"
            if not navigated:
                try:
                    next_btns = self.driver.find_elements(
                        By.XPATH,
                        '//a[text()=">"] | //a[contains(text(),"Next")] | //button[text()=">"]'
                    )
                    if next_btns:
                        self.driver.execute_script("arguments[0].click();", next_btns[0])
                        navigated = True
                        self.log(f"Clicked next (page {next_page})")
                        time.sleep(2)
                except Exception:
                    pass

            if not navigated:
                self.log(f"Pagination ended at page {page_num}")
                break

            current_page = next_page

        self.log(f"Navigated through {len(pages_html)} pages")
        return pages_html

    def _infinite_scroll(self, max_scrolls: int, wait_between_ms: int, known_urls: set = None):
        """Handle infinite scroll pagination."""
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        for i in range(max_scrolls):
            # Early exit if most jobs on page are already known
            if known_urls and i > 0 and self._should_stop_pagination(known_urls):
                break

            # Scroll to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(wait_between_ms / 1000)

            # Check if we've reached the end
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                self.log(f"Infinite scroll ended after {i + 1} scrolls")
                break

            last_height = new_height
            self.log(f"Scroll {i + 1}/{max_scrolls}")

    def _expand_sections(self):
        """Expand accordion sections or collapsible elements."""
        try:
            expand_buttons = self.driver.find_elements(
                By.CSS_SELECTOR,
                "button[aria-expanded='false'], [class*='expand'], [class*='accordion'], [class*='collapse']"
            )

            if expand_buttons:
                self.log(f"Found {len(expand_buttons)} expandable sections")
                for btn in expand_buttons[:30]:  # Limit to 30
                    try:
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                        time.sleep(0.2)
                        self.driver.execute_script("arguments[0].click();", btn)
                        time.sleep(0.3)
                    except Exception:
                        pass
                time.sleep(2)
        except Exception as e:
            self.log(f"Error expanding sections: {e}")

    # ------------------------------------------------------------------
    # Early exit: check if current page is mostly known jobs
    # ------------------------------------------------------------------

    def _should_stop_pagination(self, known_urls: set, threshold: float = 0.7) -> bool:
        """Check if most job links on the current page are already known.

        Extracts href values from job-like links and compares against
        known_urls.  Returns True when the fraction of known URLs on
        the page meets or exceeds *threshold* (default 70%).
        """
        if not known_urls or not self.driver:
            return False

        try:
            urls_on_page = self.driver.execute_script("""
                var links = document.querySelectorAll(
                    'a[href*="/job"], a[href*="/position"], a[href*="/career"], '
                  + 'a[href*="/opening"], a[href*="/jobs/"], a[href*="/requisition"]'
                );
                var urls = [];
                links.forEach(function(a) {
                    var href = a.href;
                    if (href && href.startsWith('http')) urls.push(href);
                });
                return urls;
            """)
        except Exception:
            return False

        if not urls_on_page or len(urls_on_page) < 3:
            return False

        known_on_page = sum(1 for u in urls_on_page if u in known_urls)
        ratio = known_on_page / len(urls_on_page)
        if ratio >= threshold:
            self.log(
                f"Early exit: {known_on_page}/{len(urls_on_page)} "
                f"({ratio:.0%}) job links already known"
            )
            return True
        return False

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def get_page_html(self) -> str:
        """Get current page HTML."""
        if self.driver:
            return self.driver.page_source
        return ""

    def close(self):
        """Close the browser."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
            self._network_capture_enabled = False

    def __del__(self):
        self.close()
