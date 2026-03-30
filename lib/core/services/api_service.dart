import 'package:dio/dio.dart';
import '../models/api_models.dart';

class ApiService {
  // Changes based on environment variable API_URL
  static const String baseUrl = String.fromEnvironment('API_URL', defaultValue: 'http://localhost:8080');

  final Dio _dio;

  ApiService()
      : _dio = Dio(
          BaseOptions(
            baseUrl: baseUrl,
            connectTimeout: const Duration(seconds: 15),
            receiveTimeout: const Duration(seconds: 60),
            headers: {'Content-Type': 'application/json'},
          ),
        );

  // ── Generate ──────────────────────────────────────────────────────────────

  Future<String> generate(GenerateRequest request) async {
    final resp = await _dio.post('/generate', data: request.toJson());
    return resp.data['job_id'] as String;
  }

  // ── Status ────────────────────────────────────────────────────────────────

  Future<JobStatus> getStatus(String jobId) async {
    final resp = await _dio.get('/status/$jobId');
    return JobStatus.fromJson(Map<String, dynamic>.from(resp.data));
  }

  // ── Upload ────────────────────────────────────────────────────────────────

  Future<String> uploadImage(String filePath) async {
    final form = FormData.fromMap({
      'file': await MultipartFile.fromFile(filePath),
    });
    final resp = await _dio.post('/upload', data: form);
    return resp.data['key'] as String;
  }

  // ── Export links ──────────────────────────────────────────────────────────

  Future<ExportLinks> getExportLinks(String jobId) async {
    final resp = await _dio.get('/export/$jobId/links');
    return ExportLinks.fromJson(Map<String, dynamic>.from(resp.data));
  }

  // ── Customize ─────────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> customize(
      String jobId, CustomizeRequest req) async {
    final resp =
        await _dio.post('/customize/$jobId', data: req.toJson());
    return Map<String, dynamic>.from(resp.data);
  }

  // ── Download file ─────────────────────────────────────────────────────────

  Future<String> downloadFile(String url, String savePath) async {
    await _dio.download(url, savePath);
    return savePath;
  }
}
