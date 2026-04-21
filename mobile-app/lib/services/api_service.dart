import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiService {
  // For Windows Desktop or iOS Simulator use 'localhost'
  // For Android emulator use '10.0.2.2'
  static const String baseUrl = 'http://10.0.2.2:8000';

  // ── Service Status ──────────────────────────────────────────────
  static Future<Map<String, dynamic>> getServicesStatus() async {
    try {
      final resp = await http
          .get(Uri.parse('$baseUrl/services/status'))
          .timeout(const Duration(seconds: 10));
      if (resp.statusCode == 200) {
        return Map<String, dynamic>.from(jsonDecode(resp.body));
      }
    } catch (_) {}
    return {};
  }

  // ── Load Model ──────────────────────────────────────────────────
  static Future<bool> loadModel(String serviceName) async {
    try {
      final resp = await http
          .post(Uri.parse('$baseUrl/services/$serviceName/load-model'))
          .timeout(const Duration(minutes: 10));
      return resp.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  // ── Generate Song (parallel pipeline) ───────────────────────────
  static Future<Map<String, dynamic>?> generateSong({
    required String prompt,
    required String style,
    required List<String> features,
  }) async {
    try {
      final resp = await http
          .post(
            Uri.parse('$baseUrl/generate-song'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'prompt': prompt,
              'style': style,
              'features': features,
            }),
          )
          .timeout(const Duration(minutes: 5));
      if (resp.statusCode == 200) {
        return Map<String, dynamic>.from(jsonDecode(resp.body));
      }
    } catch (_) {}
    return null;
  }

  // ── Remix ───────────────────────────────────────────────────────
  static Future<Map<String, dynamic>?> remixAudio(String filePath) async {
    try {
      final uri = Uri.parse('$baseUrl/remix');
      final request = http.MultipartRequest('POST', uri);
      request.files.add(await http.MultipartFile.fromPath('file', filePath));
      final streamedResp =
          await request.send().timeout(const Duration(minutes: 10));
      final body = await streamedResp.stream.bytesToString();
      if (streamedResp.statusCode == 200) {
        return Map<String, dynamic>.from(jsonDecode(body));
      }
    } catch (_) {}
    return null;
  }

  // ── Clone Voice ─────────────────────────────────────────────────
  static Future<String?> cloneVoice(String filePath) async {
    try {
      final uri = Uri.parse('$baseUrl/services/clone/clone-voice');
      final request = http.MultipartRequest('POST', uri);
      request.files.add(await http.MultipartFile.fromPath('file', filePath));
      final streamedResp =
          await request.send().timeout(const Duration(seconds: 60));
      final body = await streamedResp.stream.bytesToString();
      if (streamedResp.statusCode == 200) {
        final data = jsonDecode(body);
        return data['voice_profile_id'];
      }
    } catch (_) {}
    return null;
  }

  // ── Health ──────────────────────────────────────────────────────
  static Future<bool> checkHealth() async {
    try {
      final resp = await http
          .get(Uri.parse('$baseUrl/health'))
          .timeout(const Duration(seconds: 5));
      return resp.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  // ── Audio URL helper ────────────────────────────────────────────
  static String audioUrl(String filename) => '$baseUrl/outputs/$filename';
}
