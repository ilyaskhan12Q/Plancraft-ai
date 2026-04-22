import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../core/providers/providers.dart';
import '../../core/theme/app_theme.dart';


class ResultsScreen extends ConsumerWidget {
  const ResultsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final status = ref.watch(jobStatusProvider);
    final variant = status?.variants.isNotEmpty == true
        ? status!.variants.first
        : null;

    return Scaffold(
      backgroundColor: AppTheme.black,
      appBar: AppBar(
        title: const Text('Your Design'),
        leading: BackButton(onPressed: () => context.go('/input')),
        actions: [
          IconButton(
            icon: const Icon(Icons.download_outlined, color: AppTheme.gold),
            onPressed: () => context.push('/export'),
            tooltip: 'Export',
          ),
        ],
      ),
      body: status == null
          ? const Center(
              child: Text('No results yet.',
                  style: TextStyle(color: AppTheme.greyLight)))
          : SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 2D Floor Plan
                  _ResultSection(
                    title: '🗺 2D Floor Plan',
                    subtitle: '150 DPI · Printable A3',
                    child: variant?.floorplanUrl != null
                        ? _ImageCard(url: variant!.floorplanUrl!)
                        : const _Placeholder('Floor plan not available'),
                  ),
                  const SizedBox(height: 24),
                  // 3D Render
                  _ResultSection(
                    title: '🏠 3D Exterior Render',
                    subtitle: '1920×1080 · Cycles 128 samples',
                    child: variant?.renderUrl != null
                        ? _ImageCard(url: variant!.renderUrl!, tall: true)
                        : const _Placeholder('3D render not available'),
                  ),
                  const SizedBox(height: 32),
                  // Action buttons
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          icon: const Icon(Icons.view_in_ar),
                          label: const Text('View in AR'),
                          onPressed: variant?.modelUrl != null
                              ? () => context.push('/viewer',
                                  extra: variant!.modelUrl)
                              : null,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: OutlinedButton.icon(
                          icon: const Icon(Icons.palette_outlined),
                          label: const Text('Customise'),
                          onPressed: () => context.push('/customize'),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      icon: const Icon(Icons.download),
                      label: const Text('Download All Files'),
                      onPressed: () => context.push('/export'),
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}

class _ResultSection extends StatelessWidget {
  const _ResultSection({
    required this.title,
    required this.subtitle,
    required this.child,
  });
  final String title, subtitle;
  final Widget child;

  @override
  Widget build(BuildContext context) => Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title,
              style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w700,
                  color: AppTheme.white)),
          const SizedBox(height: 2),
          Text(subtitle,
              style: const TextStyle(fontSize: 12, color: AppTheme.grey)),
          const SizedBox(height: 10),
          child,
        ],
      );
}

class _ImageCard extends StatelessWidget {
  const _ImageCard({required this.url, this.tall = false});
  final String url;
  final bool tall;

  @override
  Widget build(BuildContext context) => ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: CachedNetworkImage(
          imageUrl: url,
          height: tall ? 240 : 180,
          width: double.infinity,
          fit: BoxFit.cover,
          placeholder: (_, __) => Container(
            height: tall ? 240 : 180,
            color: AppTheme.cardColor,
            child: const Center(
                child: CircularProgressIndicator(color: AppTheme.gold)),
          ),
          errorWidget: (_, __, ___) => Container(
            height: tall ? 240 : 180,
            color: AppTheme.cardColor,
            child: const Center(
                child: Text('Image unavailable',
                    style: TextStyle(color: AppTheme.greyLight))),
          ),
        ),
      );
}

class _Placeholder extends StatelessWidget {
  const _Placeholder(this.msg);
  final String msg;

  @override
  Widget build(BuildContext context) => Container(
        height: 160,
        decoration: BoxDecoration(
          color: AppTheme.cardColor,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: const Color(0xFF2A2A2A)),
        ),
        child: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.image_not_supported_outlined,
                  color: AppTheme.grey),
              const SizedBox(height: 8),
              Text(msg,
                  style: const TextStyle(color: AppTheme.grey, fontSize: 13)),
            ],
          ),
        ),
      );
}
