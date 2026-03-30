import 'package:flutter/material.dart';
import 'package:model_viewer_plus/model_viewer_plus.dart';
import '../../core/theme/app_theme.dart';

class ViewerScreen extends StatelessWidget {
  const ViewerScreen({super.key, required this.modelUrl});
  final String modelUrl;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.black,
      appBar: AppBar(
        title: const Text('3D Viewer'),
        actions: [
          IconButton(
            icon: const Icon(Icons.fullscreen, color: AppTheme.gold),
            onPressed: () {},
            tooltip: 'Fullscreen',
          ),
        ],
      ),
      body: modelUrl.isEmpty
          ? const Center(
              child: Text('No model available',
                  style: TextStyle(color: AppTheme.greyLight)))
          : Column(
              children: [
                Expanded(
                  child: ModelViewer(
                    src: modelUrl,
                    alt: '3D building model',
                    ar: true,
                    autoRotate: true,
                    cameraControls: true,
                    backgroundColor: const Color(0xFF0A0A0A),
                  ),
                ),
                Container(
                  color: AppTheme.cardColor,
                  padding: const EdgeInsets.symmetric(
                      horizontal: 20, vertical: 12),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      _Hint(icon: Icons.touch_app, label: 'Drag to rotate'),
                      _Hint(icon: Icons.pinch, label: 'Pinch to zoom'),
                      _Hint(
                          icon: Icons.view_in_ar, label: 'Tap AR to view live'),
                    ],
                  ),
                ),
              ],
            ),
    );
  }
}

class _Hint extends StatelessWidget {
  const _Hint({required this.icon, required this.label});
  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) => Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: AppTheme.gold, size: 20),
          const SizedBox(height: 4),
          Text(label,
              style:
                  const TextStyle(fontSize: 11, color: AppTheme.greyLight)),
        ],
      );
}
