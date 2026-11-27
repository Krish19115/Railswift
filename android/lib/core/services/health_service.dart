import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config/api_config.dart';
import '../models/health_status.dart';

class HealthService {
  HealthService({http.Client? client}) : _client = client ?? http.Client();

  final http.Client _client;

  Future<HealthStatus> fetch() async {
    final uri = Uri.parse('${ApiConfig.baseUrl}/health/');
    final response = await _client.get(uri).timeout(const Duration(seconds: 5));
    if (response.statusCode != 200 && response.statusCode != 503) {
      throw Exception('API returned ${response.statusCode}');
    }
    return HealthStatus.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  void close() => _client.close();
}
