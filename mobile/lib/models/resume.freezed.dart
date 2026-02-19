// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'resume.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
  'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models',
);

Resume _$ResumeFromJson(Map<String, dynamic> json) {
  return _Resume.fromJson(json);
}

/// @nodoc
mixin _$Resume {
  int get id => throw _privateConstructorUsedError;
  int get userId => throw _privateConstructorUsedError;
  String get fileName => throw _privateConstructorUsedError;
  String get filePath => throw _privateConstructorUsedError;
  Map<String, dynamic>? get parsedData => throw _privateConstructorUsedError;
  DateTime get uploadedAt => throw _privateConstructorUsedError;

  /// Serializes this Resume to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of Resume
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ResumeCopyWith<Resume> get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ResumeCopyWith<$Res> {
  factory $ResumeCopyWith(Resume value, $Res Function(Resume) then) =
      _$ResumeCopyWithImpl<$Res, Resume>;
  @useResult
  $Res call({
    int id,
    int userId,
    String fileName,
    String filePath,
    Map<String, dynamic>? parsedData,
    DateTime uploadedAt,
  });
}

/// @nodoc
class _$ResumeCopyWithImpl<$Res, $Val extends Resume>
    implements $ResumeCopyWith<$Res> {
  _$ResumeCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of Resume
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? userId = null,
    Object? fileName = null,
    Object? filePath = null,
    Object? parsedData = freezed,
    Object? uploadedAt = null,
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
            fileName:
                null == fileName
                    ? _value.fileName
                    : fileName // ignore: cast_nullable_to_non_nullable
                        as String,
            filePath:
                null == filePath
                    ? _value.filePath
                    : filePath // ignore: cast_nullable_to_non_nullable
                        as String,
            parsedData:
                freezed == parsedData
                    ? _value.parsedData
                    : parsedData // ignore: cast_nullable_to_non_nullable
                        as Map<String, dynamic>?,
            uploadedAt:
                null == uploadedAt
                    ? _value.uploadedAt
                    : uploadedAt // ignore: cast_nullable_to_non_nullable
                        as DateTime,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$ResumeImplCopyWith<$Res> implements $ResumeCopyWith<$Res> {
  factory _$$ResumeImplCopyWith(
    _$ResumeImpl value,
    $Res Function(_$ResumeImpl) then,
  ) = __$$ResumeImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    int id,
    int userId,
    String fileName,
    String filePath,
    Map<String, dynamic>? parsedData,
    DateTime uploadedAt,
  });
}

/// @nodoc
class __$$ResumeImplCopyWithImpl<$Res>
    extends _$ResumeCopyWithImpl<$Res, _$ResumeImpl>
    implements _$$ResumeImplCopyWith<$Res> {
  __$$ResumeImplCopyWithImpl(
    _$ResumeImpl _value,
    $Res Function(_$ResumeImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of Resume
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? userId = null,
    Object? fileName = null,
    Object? filePath = null,
    Object? parsedData = freezed,
    Object? uploadedAt = null,
  }) {
    return _then(
      _$ResumeImpl(
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
        fileName:
            null == fileName
                ? _value.fileName
                : fileName // ignore: cast_nullable_to_non_nullable
                    as String,
        filePath:
            null == filePath
                ? _value.filePath
                : filePath // ignore: cast_nullable_to_non_nullable
                    as String,
        parsedData:
            freezed == parsedData
                ? _value._parsedData
                : parsedData // ignore: cast_nullable_to_non_nullable
                    as Map<String, dynamic>?,
        uploadedAt:
            null == uploadedAt
                ? _value.uploadedAt
                : uploadedAt // ignore: cast_nullable_to_non_nullable
                    as DateTime,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$ResumeImpl implements _Resume {
  const _$ResumeImpl({
    required this.id,
    required this.userId,
    required this.fileName,
    required this.filePath,
    final Map<String, dynamic>? parsedData,
    required this.uploadedAt,
  }) : _parsedData = parsedData;

  factory _$ResumeImpl.fromJson(Map<String, dynamic> json) =>
      _$$ResumeImplFromJson(json);

  @override
  final int id;
  @override
  final int userId;
  @override
  final String fileName;
  @override
  final String filePath;
  final Map<String, dynamic>? _parsedData;
  @override
  Map<String, dynamic>? get parsedData {
    final value = _parsedData;
    if (value == null) return null;
    if (_parsedData is EqualUnmodifiableMapView) return _parsedData;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  final DateTime uploadedAt;

  @override
  String toString() {
    return 'Resume(id: $id, userId: $userId, fileName: $fileName, filePath: $filePath, parsedData: $parsedData, uploadedAt: $uploadedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ResumeImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.userId, userId) || other.userId == userId) &&
            (identical(other.fileName, fileName) ||
                other.fileName == fileName) &&
            (identical(other.filePath, filePath) ||
                other.filePath == filePath) &&
            const DeepCollectionEquality().equals(
              other._parsedData,
              _parsedData,
            ) &&
            (identical(other.uploadedAt, uploadedAt) ||
                other.uploadedAt == uploadedAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    id,
    userId,
    fileName,
    filePath,
    const DeepCollectionEquality().hash(_parsedData),
    uploadedAt,
  );

  /// Create a copy of Resume
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ResumeImplCopyWith<_$ResumeImpl> get copyWith =>
      __$$ResumeImplCopyWithImpl<_$ResumeImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ResumeImplToJson(this);
  }
}

abstract class _Resume implements Resume {
  const factory _Resume({
    required final int id,
    required final int userId,
    required final String fileName,
    required final String filePath,
    final Map<String, dynamic>? parsedData,
    required final DateTime uploadedAt,
  }) = _$ResumeImpl;

  factory _Resume.fromJson(Map<String, dynamic> json) = _$ResumeImpl.fromJson;

  @override
  int get id;
  @override
  int get userId;
  @override
  String get fileName;
  @override
  String get filePath;
  @override
  Map<String, dynamic>? get parsedData;
  @override
  DateTime get uploadedAt;

  /// Create a copy of Resume
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ResumeImplCopyWith<_$ResumeImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
