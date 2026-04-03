import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import '../../core/providers/providers.dart';
import '../../core/theme/app_theme.dart';

// Web-specific imports handled conditionally
import 'export_web.dart' if (dart.library.io) 'export_native.dart' as platform;

class ExportScreen extends ConsumerStatefulWidget {
  const ExportScreen({super.key});

  @override
  ConsumerState<ExportScreen> createState() => _ExportScreenState();
}

class _ExportScreenState extends ConsumerState<ExportScreen> {
  final Set<String> _downloading = {};

  Future<void> _download(String label, String? url, String filename) async {
    if (url == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('File not available yet')));
      return;
    }
    setState(() => _downloading.add(label));
    try {
      await platform.downloadFile(url, filename);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('$label download started!')));
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Download failed: $e')));
      }
    } finally {
      if (mounted) setState(() => _downloading.remove(label));
    }
  }

  @override
  Widget build(BuildContext context) {
    final status = ref.watch(jobStatusProvider);
    final variant = status?.variants.isNotEmpty == true
        ? status!.variants.first
        : null;

    final List<_ExportFile> files = [];

    if (variant != null) {
      // 2D Floor Plans
      if (variant.floorplanUrls.isNotEmpty) {
        for (int i = 0; i < variant.floorplanUrls.length; i++) {
          files.add(_ExportFile(
            label: 'Floor $i Plan',
            icon: Icons.map_outlined,
            ext: 'PNG',
            desc: '200 DPI — Floor $i Layout',
            url: variant.floorplanUrls[i],
            filename: 'floor_${i}_plan.png',
          ));
        }
      } else {
        files.add(_ExportFile(
          label: '2D Floor Plan',
          icon: Icons.map_outlined,
          ext: 'PNG',
          desc: '200 DPI — printable A3',
          url: variant.floorplanUrl,
          filename: 'floor_plan.png',
        ));
      }

      // Professional CAD
      if (variant.cadUrls.isNotEmpty) {
        for (int i = 0; i < variant.cadUrls.length; i++) {
          files.add(_ExportFile(
            label: 'Floor $i CAD',
            icon: Icons.architecture,
            ext: 'DXF',
            desc: 'NanoCAD & Blender Compatible',
            url: variant.cadUrls[i],
            filename: 'floor_${i}_plan.dxf',
          ));
        }
      } else {
        files.add(_ExportFile(
          label: 'Professional CAD',
          icon: Icons.architecture,
          ext: 'DXF',
          desc: 'NanoCAD & Blender Compatible',
          url: variant.dxfUrl,
          filename: 'floor_plan.dxf',
        ));
      }

      // 3D Render
      files.add(_ExportFile(
        label: '3D Render',
        icon: Icons.image_outlined,
        ext: 'PNG',
        desc: '1920×1080 — Cycles export',
        url: variant.renderUrl,
        filename: 'render.png',
      ));

      // 3D Model
      files.add(_ExportFile(
        label: '3D Model',
        icon: Icons.view_in_ar,
        ext: 'GLB',
        desc: 'GLTF binary — AR / Unity',
        url: variant.modelUrl,
        filename: 'model.glb',
      ));

      // 3D Print File
      files.add(_ExportFile(
        label: '3D Print File',
        icon: Icons.print_outlined,
        ext: 'STL',
        desc: 'FDM / resin printers',
        url: variant.stlUrl,
        filename: 'model.stl',
      ));
    }

    return Scaffold(
      backgroundColor: AppTheme.black,
      appBar: AppBar(title: const Text('Export & Download')),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Your design files are ready.',
              style: TextStyle(
                  fontSize: 16,
                  color: AppTheme.greyLight,
                  height: 1.5),
            ),
            const SizedBox(height: 24),
            Expanded(
              child: ListView.separated(
                itemCount: files.length,
                separatorBuilder: (_, __) => const SizedBox(height: 12),
                itemBuilder: (_, i) {
                  final f = files[i];
                  final loading = _downloading.contains(f.label);
                  final available = f.url != null;
                  return _ExportCard(
                    file: f,
                    loading: loading,
                    available: available,
                    onTap: available && !loading
                        ? () => _download(f.label, f.url, f.filename)
                        : null,
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ExportFile {
  const _ExportFile({
    required this.label,
    required this.icon,
    required this.ext,
    required this.desc,
    required this.url,
    required this.filename,
  });
  final String label, ext, desc, filename;
  final String? url;
  final IconData icon;
}

class _ExportCard extends StatelessWidget {
  const _ExportCard({
    required this.file,
    required this.loading,
    required this.available,
    this.onTap,
  });
  final _ExportFile file;
  final bool loading, available;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) => GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppTheme.cardColor,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: available
                  ? AppTheme.gold.withOpacity(0.4)
                  : const Color(0xFF2A2A2A),
            ),
          ),
          child: Row(
            children: [
              Container(
                width: 52, height: 52,
                decoration: BoxDecoration(
                  color: available
                      ? AppTheme.gold.withOpacity(0.15)
                      : AppTheme.black,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(file.icon,
                    color: available ? AppTheme.gold : AppTheme.grey,
                    size: 26),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(file.label,
                        style: TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.w700,
                            color: available
                                ? AppTheme.white
                                : AppTheme.grey)),
                    const SizedBox(height: 2),
                    Text(file.desc,
                        style: const TextStyle(
                            fontSize: 12, color: AppTheme.grey)),
                  ],
                ),
              ),
              if (loading)
                const SizedBox(
                    width: 22, height: 22,
                    child: CircularProgressIndicator(
                        color: AppTheme.gold, strokeWidth: 2))
              else if (available)
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 10, vertical: 5),
                  decoration: BoxDecoration(
                    gradient: kGoldGradient,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(file.ext,
                      style: const TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w800,
                          color: AppTheme.black)),
                )
              else
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 10, vertical: 5),
                  decoration: BoxDecoration(
                    color: AppTheme.black,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Text('N/A',
                      style: TextStyle(
                          fontSize: 11, color: AppTheme.grey)),
                ),
            ],
          ),
        ),
      );
}
