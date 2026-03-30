// Web-specific download implementation
// ignore: avoid_web_libraries_in_flutter
import 'dart:html' as html;

Future<void> downloadFile(String url, String filename) async {
  // Open in a new tab to trigger browser download
  final anchor = html.AnchorElement(href: url)
    ..setAttribute('download', filename)
    ..setAttribute('target', '_blank');
  html.document.body?.append(anchor);
  anchor.click();
  anchor.remove();
}
