class BackendHttpException implements Exception {
  const BackendHttpException({
    required this.statusCode,
    required this.message,
  });

  final int statusCode;
  final String message;

  bool get isServiceUnavailable => statusCode == 503 || statusCode == 504;

  @override
  String toString() => 'BackendHttpException($statusCode): $message';
}

class NoHealthyMagnetException implements Exception {
  const NoHealthyMagnetException(this.message);

  final String message;

  @override
  String toString() => 'NoHealthyMagnetException: $message';
}

class NoInternetException implements Exception {
  const NoInternetException(this.message);

  final String message;

  @override
  String toString() => 'NoInternetException: $message';
}
