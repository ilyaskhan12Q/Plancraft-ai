import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../core/providers/providers.dart';
import '../../core/theme/app_theme.dart';
import '../../core/models/api_models.dart';


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
                  // 2D Floor Plan(s)
                  _ResultSection(
                    title: '🗺 2D Floor Plans',
                    subtitle: 'Architectural Details · Professional Grade',
                    child: variant != null && variant.previews.isNotEmpty
                        ? Column(
                            children: variant.previews
                                .asMap()
                                .entries
                                .map((entry) => Padding(
                                      padding: const EdgeInsets.only(bottom: 16),
                                      child: Column(
                                        crossAxisAlignment:
                                            CrossAxisAlignment.start,
                                        children: [
                                          Text(
                                            'Floor ${entry.key}',
                                            style: const TextStyle(
                                                fontSize: 12,
                                                color: AppTheme.gold,
                                                fontWeight: FontWeight.w600),
                                          ),
                                          const SizedBox(height: 8),
                                          _ImageCard(url: entry.value),
                                        ],
                                      ),
                                    ))
                                .toList(),
                          )
                        : variant?.floorplanUrl != null
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
                  const SizedBox(height: 24),
                  // Cost Estimate Card
                  if (status.costEstimate != null)
                    _CostEstimateCard(estimate: status.costEstimate!),
                  if (status.costEstimate != null) const SizedBox(height: 24),
                  // Architect's Notes
                  if (status.critique.isNotEmpty)
                    _ArchitectNotesCard(notes: status.critique),
                  if (status.critique.isNotEmpty) const SizedBox(height: 24),
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

// ── Cost Estimate Card ────────────────────────────────────────────────────────

class _CostEstimateCard extends StatelessWidget {
  const _CostEstimateCard({required this.estimate});
  final CostEstimate estimate;

  @override
  Widget build(BuildContext context) {
    final boq = estimate.boq;
    return Container(
      decoration: BoxDecoration(
        color: AppTheme.cardColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.gold.withOpacity(0.3)),
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.calculate_outlined, color: AppTheme.gold, size: 20),
              const SizedBox(width: 8),
              const Text('💰 Cost Estimate',
                  style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      color: AppTheme.white)),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            '${estimate.coveredAreaSqm.toStringAsFixed(0)} m²  ·  ${estimate.coveredAreaSqft.toStringAsFixed(0)} sqft covered',
            style: const TextStyle(fontSize: 12, color: AppTheme.grey),
          ),
          const SizedBox(height: 16),
          // Cost tiers
          Row(
            children: [
              _CostTile(label: 'Budget', value: estimate.lowFormatted,
                  color: Colors.green.shade400),
              const SizedBox(width: 8),
              _CostTile(label: 'Standard', value: estimate.midFormatted,
                  color: AppTheme.gold, highlight: true),
              const SizedBox(width: 8),
              _CostTile(label: 'Premium', value: estimate.highFormatted,
                  color: Colors.purple.shade300),
            ],
          ),
          const SizedBox(height: 4),
          Text('≈ ${estimate.usdFormatted} USD (standard)',
              style: const TextStyle(fontSize: 11, color: AppTheme.grey)),
          const Divider(color: Color(0xFF2A2A2A), height: 24),
          // Bill of Quantities
          const Text('📋 Bill of Quantities',
              style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: AppTheme.greyLight)),
          const SizedBox(height: 10),
          Wrap(
            spacing: 10,
            runSpacing: 8,
            children: [
              _BoqChip(label: 'Bricks', value: '${boq.bricks}'),
              _BoqChip(label: 'Cement', value: '${boq.cementBags} bags'),
              _BoqChip(label: 'Steel', value: '${boq.steelKg} kg'),
              _BoqChip(label: 'Paint', value: '${boq.paintLiters} L'),
              _BoqChip(label: 'Sand', value: '${boq.sandCubicMeters} m³'),
            ],
          ),
        ],
      ),
    );
  }
}

class _CostTile extends StatelessWidget {
  const _CostTile(
      {required this.label,
      required this.value,
      required this.color,
      this.highlight = false});
  final String label, value;
  final Color color;
  final bool highlight;

  @override
  Widget build(BuildContext context) => Expanded(
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 8),
          decoration: BoxDecoration(
            color: highlight
                ? color.withOpacity(0.12)
                : const Color(0xFF1A1A1A),
            borderRadius: BorderRadius.circular(10),
            border: highlight
                ? Border.all(color: color.withOpacity(0.5))
                : null,
          ),
          child: Column(
            children: [
              Text(label,
                  style:
                      TextStyle(fontSize: 10, color: color.withOpacity(0.8))),
              const SizedBox(height: 4),
              FittedBox(
                child: Text(value,
                    style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w700,
                        color: color)),
              ),
            ],
          ),
        ),
      );
}

class _BoqChip extends StatelessWidget {
  const _BoqChip({required this.label, required this.value});
  final String label, value;

  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          color: const Color(0xFF1A1A1A),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(value,
                style: const TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: AppTheme.white)),
            Text(label,
                style:
                    const TextStyle(fontSize: 10, color: AppTheme.grey)),
          ],
        ),
      );
}

// ── Architect's Notes Card ────────────────────────────────────────────────────

class _ArchitectNotesCard extends StatefulWidget {
  const _ArchitectNotesCard({required this.notes});
  final List<String> notes;

  @override
  State<_ArchitectNotesCard> createState() => _ArchitectNotesCardState();
}

class _ArchitectNotesCardState extends State<_ArchitectNotesCard> {
  bool _expanded = true;

  @override
  Widget build(BuildContext context) => Container(
        decoration: BoxDecoration(
          color: AppTheme.cardColor,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: const Color(0xFF2A2A2A)),
        ),
        child: Column(
          children: [
            InkWell(
              onTap: () => setState(() => _expanded = !_expanded),
              borderRadius: BorderRadius.circular(16),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    const Icon(Icons.architecture, color: AppTheme.gold, size: 20),
                    const SizedBox(width: 8),
                    const Expanded(
                      child: Text('🏗 Architect\'s Notes',
                          style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w700,
                              color: AppTheme.white)),
                    ),
                    Icon(
                      _expanded
                          ? Icons.keyboard_arrow_up
                          : Icons.keyboard_arrow_down,
                      color: AppTheme.grey,
                    ),
                  ],
                ),
              ),
            ),
            if (_expanded)
              Padding(
                padding:
                    const EdgeInsets.only(left: 16, right: 16, bottom: 16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: widget.notes
                      .map((note) => Padding(
                            padding: const EdgeInsets.only(bottom: 10),
                            child: Text(note,
                                style: const TextStyle(
                                    fontSize: 13,
                                    color: AppTheme.greyLight,
                                    height: 1.5)),
                          ))
                      .toList(),
                ),
              ),
          ],
        ),
      );
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
