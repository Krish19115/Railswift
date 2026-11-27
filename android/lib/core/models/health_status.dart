class HealthStatus {
  const HealthStatus({required this.status, required this.database});

  final String status;
  final String database;

  factory HealthStatus.fromJson(Map<String, dynamic> json) => HealthStatus(
        status: json['status'] as String? ?? 'degraded',
        database: json['database'] as String? ?? 'unavailable',
      );
}
