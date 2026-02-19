// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'scrape_config.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
  'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models',
);

ScrapeConfig _$ScrapeConfigFromJson(Map<String, dynamic> json) {
  return _ScrapeConfig.fromJson(json);
}

/// @nodoc
mixin _$ScrapeConfig {
  int get id => throw _privateConstructorUsedError;
  int get userId => throw _privateConstructorUsedError;
  String get name => throw _privateConstructorUsedError;
  String get platform => throw _privateConstructorUsedError;
  Map<String, dynamic> get searchParams => throw _privateConstructorUsedError;
  bool get isActive => throw _privateConstructorUsedError;
  String? get schedule => throw _privateConstructorUsedError;
  DateTime? get lastRun => throw _privateConstructorUsedError;
  DateTime get createdAt => throw _privateConstructorUsedError;
  DateTime get updatedAt => throw _privateConstructorUsedError;

  /// Serializes this ScrapeConfig to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ScrapeConfig
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ScrapeConfigCopyWith<ScrapeConfig> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ScrapeConfigCopyWith<$Res> {
  factory $ScrapeConfigCopyWith(
    ScrapeConfig value,
    $Res Function(ScrapeConfig) then,
  ) = _$ScrapeConfigCopyWithImpl<$Res, ScrapeConfig>;
  @useResult
  $Res call({
    int id,
    int userId,
    String name,
    String platform,
    Map<String, dynamic> searchParams,
    bool isActive,
    String? schedule,
    DateTime? lastRun,
    DateTime createdAt,
    DateTime updatedAt,
  });
}

/// @nodoc
class _$ScrapeConfigCopyWithImpl<$Res, $Val extends ScrapeConfig>
    implements $ScrapeConfigCopyWith<$Res> {
  _$ScrapeConfigCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ScrapeConfig
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? userId = null,
    Object? name = null,
    Object? platform = null,
    Object? searchParams = null,
    Object? isActive = null,
    Object? schedule = freezed,
    Object? lastRun = freezed,
    Object? createdAt = null,
    Object? updatedAt = null,
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
            name:
                null == name
                    ? _value.name
                    : name // ignore: cast_nullable_to_non_nullable
                        as String,
            platform:
                null == platform
                    ? _value.platform
                    : platform // ignore: cast_nullable_to_non_nullable
                        as String,
            searchParams:
                null == searchParams
                    ? _value.searchParams
                    : searchParams // ignore: cast_nullable_to_non_nullable
                        as Map<String, dynamic>,
            isActive:
                null == isActive
                    ? _value.isActive
                    : isActive // ignore: cast_nullable_to_non_nullable
                        as bool,
            schedule:
                freezed == schedule
                    ? _value.schedule
                    : schedule // ignore: cast_nullable_to_non_nullable
                        as String?,
            lastRun:
                freezed == lastRun
                    ? _value.lastRun
                    : lastRun // ignore: cast_nullable_to_non_nullable
                        as DateTime?,
            createdAt:
                null == createdAt
                    ? _value.createdAt
                    : createdAt // ignore: cast_nullable_to_non_nullable
                        as DateTime,
            updatedAt:
                null == updatedAt
                    ? _value.updatedAt
                    : updatedAt // ignore: cast_nullable_to_non_nullable
                        as DateTime,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$ScrapeConfigImplCopyWith<$Res>
    implements $ScrapeConfigCopyWith<$Res> {
  factory _$$ScrapeConfigImplCopyWith(
    _$ScrapeConfigImpl value,
    $Res Function(_$ScrapeConfigImpl) then,
  ) = __$$ScrapeConfigImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    int id,
    int userId,
    String name,
    String platform,
    Map<String, dynamic> searchParams,
    bool isActive,
    String? schedule,
    DateTime? lastRun,
    DateTime createdAt,
    DateTime updatedAt,
  });
}

/// @nodoc
class __$$ScrapeConfigImplCopyWithImpl<$Res>
    extends _$ScrapeConfigCopyWithImpl<$Res, _$ScrapeConfigImpl>
    implements _$$ScrapeConfigImplCopyWith<$Res> {
  __$$ScrapeConfigImplCopyWithImpl(
    _$ScrapeConfigImpl _value,
    $Res Function(_$ScrapeConfigImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of ScrapeConfig
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? userId = null,
    Object? name = null,
    Object? platform = null,
    Object? searchParams = null,
    Object? isActive = null,
    Object? schedule = freezed,
    Object? lastRun = freezed,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(
      _$ScrapeConfigImpl(
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
        name:
            null == name
                ? _value.name
                : name // ignore: cast_nullable_to_non_nullable
                    as String,
        platform:
            null == platform
                ? _value.platform
                : platform // ignore: cast_nullable_to_non_nullable
                    as String,
        searchParams:
            null == searchParams
                ? _value._searchParams
                : searchParams // ignore: cast_nullable_to_non_nullable
                    as Map<String, dynamic>,
        isActive:
            null == isActive
                ? _value.isActive
                : isActive // ignore: cast_nullable_to_non_nullable
                    as bool,
        schedule:
            freezed == schedule
                ? _value.schedule
                : schedule // ignore: cast_nullable_to_non_nullable
                    as String?,
        lastRun:
            freezed == lastRun
                ? _value.lastRun
                : lastRun // ignore: cast_nullable_to_non_nullable
                    as DateTime?,
        createdAt:
            null == createdAt
                ? _value.createdAt
                : createdAt // ignore: cast_nullable_to_non_nullable
                    as DateTime,
        updatedAt:
            null == updatedAt
                ? _value.updatedAt
                : updatedAt // ignore: cast_nullable_to_non_nullable
                    as DateTime,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$ScrapeConfigImpl implements _ScrapeConfig {
  const _$ScrapeConfigImpl({
    required this.id,
    required this.userId,
    required this.name,
    required this.platform,
    required final Map<String, dynamic> searchParams,
    required this.isActive,
    this.schedule,
    this.lastRun,
    required this.createdAt,
    required this.updatedAt,
  }) : _searchParams = searchParams;

  factory _$ScrapeConfigImpl.fromJson(Map<String, dynamic> json) =>
      _$$ScrapeConfigImplFromJson(json);

  @override
  final int id;
  @override
  final int userId;
  @override
  final String name;
  @override
  final String platform;
  final Map<String, dynamic> _searchParams;
  @override
  Map<String, dynamic> get searchParams {
    if (_searchParams is EqualUnmodifiableMapView) return _searchParams;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_searchParams);
  }

  @override
  final bool isActive;
  @override
  final String? schedule;
  @override
  final DateTime? lastRun;
  @override
  final DateTime createdAt;
  @override
  final DateTime updatedAt;

  @override
  String toString() {
    return 'ScrapeConfig(id: $id, userId: $userId, name: $name, platform: $platform, searchParams: $searchParams, isActive: $isActive, schedule: $schedule, lastRun: $lastRun, createdAt: $createdAt, updatedAt: $updatedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ScrapeConfigImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.userId, userId) || other.userId == userId) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.platform, platform) ||
                other.platform == platform) &&
            const DeepCollectionEquality().equals(
              other._searchParams,
              _searchParams,
            ) &&
            (identical(other.isActive, isActive) ||
                other.isActive == isActive) &&
            (identical(other.schedule, schedule) ||
                other.schedule == schedule) &&
            (identical(other.lastRun, lastRun) || other.lastRun == lastRun) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    id,
    userId,
    name,
    platform,
    const DeepCollectionEquality().hash(_searchParams),
    isActive,
    schedule,
    lastRun,
    createdAt,
    updatedAt,
  );

  /// Create a copy of ScrapeConfig
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ScrapeConfigImplCopyWith<_$ScrapeConfigImpl> get copyWith =>
      __$$ScrapeConfigImplCopyWithImpl<_$ScrapeConfigImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ScrapeConfigImplToJson(this);
  }
}

abstract class _ScrapeConfig implements ScrapeConfig {
  const factory _ScrapeConfig({
    required final int id,
    required final int userId,
    required final String name,
    required final String platform,
    required final Map<String, dynamic> searchParams,
    required final bool isActive,
    final String? schedule,
    final DateTime? lastRun,
    required final DateTime createdAt,
    required final DateTime updatedAt,
  }) = _$ScrapeConfigImpl;

  factory _ScrapeConfig.fromJson(Map<String, dynamic> json) =
      _$ScrapeConfigImpl.fromJson;

  @override
  int get id;
  @override
  int get userId;
  @override
  String get name;
  @override
  String get platform;
  @override
  Map<String, dynamic> get searchParams;
  @override
  bool get isActive;
  @override
  String? get schedule;
  @override
  DateTime? get lastRun;
  @override
  DateTime get createdAt;
  @override
  DateTime get updatedAt;

  /// Create a copy of ScrapeConfig
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ScrapeConfigImplCopyWith<_$ScrapeConfigImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
