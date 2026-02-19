// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'job.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
  'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models',
);

Job _$JobFromJson(Map<String, dynamic> json) {
  return _Job.fromJson(json);
}

/// @nodoc
mixin _$Job {
  int get id => throw _privateConstructorUsedError;
  int get userId => throw _privateConstructorUsedError;
  String get title => throw _privateConstructorUsedError;
  String get company => throw _privateConstructorUsedError;
  String? get location => throw _privateConstructorUsedError;
  String? get description => throw _privateConstructorUsedError;
  String? get url => throw _privateConstructorUsedError;
  String? get salary => throw _privateConstructorUsedError;
  String? get jobType => throw _privateConstructorUsedError;
  String? get seniority => throw _privateConstructorUsedError;
  String get source => throw _privateConstructorUsedError;
  String? get sourceJobId => throw _privateConstructorUsedError;
  DateTime? get postedDate => throw _privateConstructorUsedError;
  DateTime get scrapedAt => throw _privateConstructorUsedError;
  double? get matchScore => throw _privateConstructorUsedError;
  Map<String, dynamic>? get matchReasons => throw _privateConstructorUsedError;
  Map<String, dynamic>? get rawData => throw _privateConstructorUsedError;

  /// Serializes this Job to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of Job
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $JobCopyWith<Job> get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $JobCopyWith<$Res> {
  factory $JobCopyWith(Job value, $Res Function(Job) then) =
      _$JobCopyWithImpl<$Res, Job>;
  @useResult
  $Res call({
    int id,
    int userId,
    String title,
    String company,
    String? location,
    String? description,
    String? url,
    String? salary,
    String? jobType,
    String? seniority,
    String source,
    String? sourceJobId,
    DateTime? postedDate,
    DateTime scrapedAt,
    double? matchScore,
    Map<String, dynamic>? matchReasons,
    Map<String, dynamic>? rawData,
  });
}

/// @nodoc
class _$JobCopyWithImpl<$Res, $Val extends Job> implements $JobCopyWith<$Res> {
  _$JobCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of Job
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? userId = null,
    Object? title = null,
    Object? company = null,
    Object? location = freezed,
    Object? description = freezed,
    Object? url = freezed,
    Object? salary = freezed,
    Object? jobType = freezed,
    Object? seniority = freezed,
    Object? source = null,
    Object? sourceJobId = freezed,
    Object? postedDate = freezed,
    Object? scrapedAt = null,
    Object? matchScore = freezed,
    Object? matchReasons = freezed,
    Object? rawData = freezed,
  }) {
    return _then(
      _value.copyWith(
            id:
                null == id
                    ? _value.id
                    : id // ignore: cast_nullable_to_non_nullable
                        as int,
            userId:
                null == userId
                    ? _value.userId
                    : userId // ignore: cast_nullable_to_non_nullable
                        as int,
            title:
                null == title
                    ? _value.title
                    : title // ignore: cast_nullable_to_non_nullable
                        as String,
            company:
                null == company
                    ? _value.company
                    : company // ignore: cast_nullable_to_non_nullable
                        as String,
            location:
                freezed == location
                    ? _value.location
                    : location // ignore: cast_nullable_to_non_nullable
                        as String?,
            description:
                freezed == description
                    ? _value.description
                    : description // ignore: cast_nullable_to_non_nullable
                        as String?,
            url:
                freezed == url
                    ? _value.url
                    : url // ignore: cast_nullable_to_non_nullable
                        as String?,
            salary:
                freezed == salary
                    ? _value.salary
                    : salary // ignore: cast_nullable_to_non_nullable
                        as String?,
            jobType:
                freezed == jobType
                    ? _value.jobType
                    : jobType // ignore: cast_nullable_to_non_nullable
                        as String?,
            seniority:
                freezed == seniority
                    ? _value.seniority
                    : seniority // ignore: cast_nullable_to_non_nullable
                        as String?,
            source:
                null == source
                    ? _value.source
                    : source // ignore: cast_nullable_to_non_nullable
                        as String,
            sourceJobId:
                freezed == sourceJobId
                    ? _value.sourceJobId
                    : sourceJobId // ignore: cast_nullable_to_non_nullable
                        as String?,
            postedDate:
                freezed == postedDate
                    ? _value.postedDate
                    : postedDate // ignore: cast_nullable_to_non_nullable
                        as DateTime?,
            scrapedAt:
                null == scrapedAt
                    ? _value.scrapedAt
                    : scrapedAt // ignore: cast_nullable_to_non_nullable
                        as DateTime,
            matchScore:
                freezed == matchScore
                    ? _value.matchScore
                    : matchScore // ignore: cast_nullable_to_non_nullable
                        as double?,
            matchReasons:
                freezed == matchReasons
                    ? _value.matchReasons
                    : matchReasons // ignore: cast_nullable_to_non_nullable
                        as Map<String, dynamic>?,
            rawData:
                freezed == rawData
                    ? _value.rawData
                    : rawData // ignore: cast_nullable_to_non_nullable
                        as Map<String, dynamic>?,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$JobImplCopyWith<$Res> implements $JobCopyWith<$Res> {
  factory _$$JobImplCopyWith(_$JobImpl value, $Res Function(_$JobImpl) then) =
      __$$JobImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    int id,
    int userId,
    String title,
    String company,
    String? location,
    String? description,
    String? url,
    String? salary,
    String? jobType,
    String? seniority,
    String source,
    String? sourceJobId,
    DateTime? postedDate,
    DateTime scrapedAt,
    double? matchScore,
    Map<String, dynamic>? matchReasons,
    Map<String, dynamic>? rawData,
  });
}

/// @nodoc
class __$$JobImplCopyWithImpl<$Res> extends _$JobCopyWithImpl<$Res, _$JobImpl>
    implements _$$JobImplCopyWith<$Res> {
  __$$JobImplCopyWithImpl(_$JobImpl _value, $Res Function(_$JobImpl) _then)
    : super(_value, _then);

  /// Create a copy of Job
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? userId = null,
    Object? title = null,
    Object? company = null,
    Object? location = freezed,
    Object? description = freezed,
    Object? url = freezed,
    Object? salary = freezed,
    Object? jobType = freezed,
    Object? seniority = freezed,
    Object? source = null,
    Object? sourceJobId = freezed,
    Object? postedDate = freezed,
    Object? scrapedAt = null,
    Object? matchScore = freezed,
    Object? matchReasons = freezed,
    Object? rawData = freezed,
  }) {
    return _then(
      _$JobImpl(
        id:
            null == id
                ? _value.id
                : id // ignore: cast_nullable_to_non_nullable
                    as int,
        userId:
            null == userId
                ? _value.userId
                : userId // ignore: cast_nullable_to_non_nullable
                    as int,
        title:
            null == title
                ? _value.title
                : title // ignore: cast_nullable_to_non_nullable
                    as String,
        company:
            null == company
                ? _value.company
                : company // ignore: cast_nullable_to_non_nullable
                    as String,
        location:
            freezed == location
                ? _value.location
                : location // ignore: cast_nullable_to_non_nullable
                    as String?,
        description:
            freezed == description
                ? _value.description
                : description // ignore: cast_nullable_to_non_nullable
                    as String?,
        url:
            freezed == url
                ? _value.url
                : url // ignore: cast_nullable_to_non_nullable
                    as String?,
        salary:
            freezed == salary
                ? _value.salary
                : salary // ignore: cast_nullable_to_non_nullable
                    as String?,
        jobType:
            freezed == jobType
                ? _value.jobType
                : jobType // ignore: cast_nullable_to_non_nullable
                    as String?,
        seniority:
            freezed == seniority
                ? _value.seniority
                : seniority // ignore: cast_nullable_to_non_nullable
                    as String?,
        source:
            null == source
                ? _value.source
                : source // ignore: cast_nullable_to_non_nullable
                    as String,
        sourceJobId:
            freezed == sourceJobId
                ? _value.sourceJobId
                : sourceJobId // ignore: cast_nullable_to_non_nullable
                    as String?,
        postedDate:
            freezed == postedDate
                ? _value.postedDate
                : postedDate // ignore: cast_nullable_to_non_nullable
                    as DateTime?,
        scrapedAt:
            null == scrapedAt
                ? _value.scrapedAt
                : scrapedAt // ignore: cast_nullable_to_non_nullable
                    as DateTime,
        matchScore:
            freezed == matchScore
                ? _value.matchScore
                : matchScore // ignore: cast_nullable_to_non_nullable
                    as double?,
        matchReasons:
            freezed == matchReasons
                ? _value._matchReasons
                : matchReasons // ignore: cast_nullable_to_non_nullable
                    as Map<String, dynamic>?,
        rawData:
            freezed == rawData
                ? _value._rawData
                : rawData // ignore: cast_nullable_to_non_nullable
                    as Map<String, dynamic>?,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$JobImpl implements _Job {
  const _$JobImpl({
    required this.id,
    required this.userId,
    required this.title,
    required this.company,
    this.location,
    this.description,
    this.url,
    this.salary,
    this.jobType,
    this.seniority,
    required this.source,
    this.sourceJobId,
    this.postedDate,
    required this.scrapedAt,
    this.matchScore,
    final Map<String, dynamic>? matchReasons,
    final Map<String, dynamic>? rawData,
  }) : _matchReasons = matchReasons,
       _rawData = rawData;

  factory _$JobImpl.fromJson(Map<String, dynamic> json) =>
      _$$JobImplFromJson(json);

  @override
  final int id;
  @override
  final int userId;
  @override
  final String title;
  @override
  final String company;
  @override
  final String? location;
  @override
  final String? description;
  @override
  final String? url;
  @override
  final String? salary;
  @override
  final String? jobType;
  @override
  final String? seniority;
  @override
  final String source;
  @override
  final String? sourceJobId;
  @override
  final DateTime? postedDate;
  @override
  final DateTime scrapedAt;
  @override
  final double? matchScore;
  final Map<String, dynamic>? _matchReasons;
  @override
  Map<String, dynamic>? get matchReasons {
    final value = _matchReasons;
    if (value == null) return null;
    if (_matchReasons is EqualUnmodifiableMapView) return _matchReasons;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  final Map<String, dynamic>? _rawData;
  @override
  Map<String, dynamic>? get rawData {
    final value = _rawData;
    if (value == null) return null;
    if (_rawData is EqualUnmodifiableMapView) return _rawData;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  String toString() {
    return 'Job(id: $id, userId: $userId, title: $title, company: $company, location: $location, description: $description, url: $url, salary: $salary, jobType: $jobType, seniority: $seniority, source: $source, sourceJobId: $sourceJobId, postedDate: $postedDate, scrapedAt: $scrapedAt, matchScore: $matchScore, matchReasons: $matchReasons, rawData: $rawData)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$JobImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.userId, userId) || other.userId == userId) &&
            (identical(other.title, title) || other.title == title) &&
            (identical(other.company, company) || other.company == company) &&
            (identical(other.location, location) ||
                other.location == location) &&
            (identical(other.description, description) ||
                other.description == description) &&
            (identical(other.url, url) || other.url == url) &&
            (identical(other.salary, salary) || other.salary == salary) &&
            (identical(other.jobType, jobType) || other.jobType == jobType) &&
            (identical(other.seniority, seniority) ||
                other.seniority == seniority) &&
            (identical(other.source, source) || other.source == source) &&
            (identical(other.sourceJobId, sourceJobId) ||
                other.sourceJobId == sourceJobId) &&
            (identical(other.postedDate, postedDate) ||
                other.postedDate == postedDate) &&
            (identical(other.scrapedAt, scrapedAt) ||
                other.scrapedAt == scrapedAt) &&
            (identical(other.matchScore, matchScore) ||
                other.matchScore == matchScore) &&
            const DeepCollectionEquality().equals(
              other._matchReasons,
              _matchReasons,
            ) &&
            const DeepCollectionEquality().equals(other._rawData, _rawData));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    id,
    userId,
    title,
    company,
    location,
    description,
    url,
    salary,
    jobType,
    seniority,
    source,
    sourceJobId,
    postedDate,
    scrapedAt,
    matchScore,
    const DeepCollectionEquality().hash(_matchReasons),
    const DeepCollectionEquality().hash(_rawData),
  );

  /// Create a copy of Job
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$JobImplCopyWith<_$JobImpl> get copyWith =>
      __$$JobImplCopyWithImpl<_$JobImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$JobImplToJson(this);
  }
}

abstract class _Job implements Job {
  const factory _Job({
    required final int id,
    required final int userId,
    required final String title,
    required final String company,
    final String? location,
    final String? description,
    final String? url,
    final String? salary,
    final String? jobType,
    final String? seniority,
    required final String source,
    final String? sourceJobId,
    final DateTime? postedDate,
    required final DateTime scrapedAt,
    final double? matchScore,
    final Map<String, dynamic>? matchReasons,
    final Map<String, dynamic>? rawData,
  }) = _$JobImpl;

  factory _Job.fromJson(Map<String, dynamic> json) = _$JobImpl.fromJson;

  @override
  int get id;
  @override
  int get userId;
  @override
  String get title;
  @override
  String get company;
  @override
  String? get location;
  @override
  String? get description;
  @override
  String? get url;
  @override
  String? get salary;
  @override
  String? get jobType;
  @override
  String? get seniority;
  @override
  String get source;
  @override
  String? get sourceJobId;
  @override
  DateTime? get postedDate;
  @override
  DateTime get scrapedAt;
  @override
  double? get matchScore;
  @override
  Map<String, dynamic>? get matchReasons;
  @override
  Map<String, dynamic>? get rawData;

  /// Create a copy of Job
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$JobImplCopyWith<_$JobImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
