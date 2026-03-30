// Native (mobile/desktop) download implementation
import 'package:share_plus/share_plus.dart';
import 'package:path_provider/path_provider.dart';
import 'package:dio/dio.dart';

Future<void> downloadFile(String url, String filename) async {
  final dir = await getApplicationDocumentsDirectory();
  final path = '${dir.path}/$filename';
  await Dio().download(url, path);
  await Share.shareXFiles([XFile(path)], text: 'AI Architect: $filename');
}
