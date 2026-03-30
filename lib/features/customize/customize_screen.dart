import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_colorpicker/flutter_colorpicker.dart';
import 'package:go_router/go_router.dart';
import '../../core/models/api_models.dart';
import '../../core/providers/providers.dart';
import '../../core/theme/app_theme.dart';

class CustomizeScreen extends ConsumerStatefulWidget {
  const CustomizeScreen({super.key});

  @override
  ConsumerState<CustomizeScreen> createState() => _CustomizeScreenState();
}

class _CustomizeScreenState extends ConsumerState<CustomizeScreen> {
  Color _exteriorColor = const Color(0xFFF5F5F0);
  Color _roofColor = const Color(0xFF808080);
  String _roofType = 'flat';
  String _material = 'plaster';
  String _windowType = 'casement';
  bool _loading = false;

  static const _roofTypes = ['flat', 'gable', 'hip', 'mansard'];
  static const _materials = [
    'plaster', 'brick', 'concrete', 'wood', 'stone', 'marble'
  ];
  static const _windowTypes = ['casement', 'sliding', 'fixed', 'bay'];

  String _hexColor(Color c) {
    final r = ((c.value >> 16) & 0xFF).toRadixString(16).padLeft(2, '0');
    final g = ((c.value >> 8) & 0xFF).toRadixString(16).padLeft(2, '0');
    final b = (c.value & 0xFF).toRadixString(16).padLeft(2, '0');
    return '#$r$g$b'.toUpperCase();
  }

  void _pickColor(bool isExterior) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: AppTheme.cardColor,
        title: Text(isExterior ? 'Exterior Color' : 'Roof Color',
            style: const TextStyle(color: AppTheme.white)),
        content: BlockPicker(
          pickerColor: isExterior ? _exteriorColor : _roofColor,
          onColorChanged: (c) => setState(() {
            if (isExterior) {
              _exteriorColor = c;
            } else {
              _roofColor = c;
            }
          }),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Done', style: TextStyle(color: AppTheme.gold)),
          ),
        ],
      ),
    );
  }

  Future<void> _applyCustomization() async {
    final status = ref.read(jobStatusProvider);
    if (status == null) return;
    setState(() => _loading = true);
    try {
      final api = ref.read(apiServiceProvider);
      await api.customize(
        status.jobId,
        CustomizeRequest(
          exteriorColor: _hexColor(_exteriorColor),
          roofColor: _hexColor(_roofColor),
          roofType: _roofType,
          facadeMaterial: _material,
          windowType: _windowType,
        ),
      );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
              content: Text('Re-render started! Check results shortly.')),
        );
        context.go('/results');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.black,
      appBar: AppBar(title: const Text('Customise Design')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _SecHead('🎨 Exterior Color'),
            const SizedBox(height: 12),
            GestureDetector(
              onTap: () => _pickColor(true),
              child: Row(
                children: [
                  Container(
                    width: 48, height: 48,
                    decoration: BoxDecoration(
                      color: _exteriorColor,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: AppTheme.gold),
                    ),
                  ),
                  const SizedBox(width: 14),
                  Text(_hexColor(_exteriorColor),
                      style: const TextStyle(
                          color: AppTheme.gold, fontWeight: FontWeight.w600)),
                  const SizedBox(width: 8),
                  const Icon(Icons.edit, color: AppTheme.grey, size: 16),
                ],
              ),
            ),
            const SizedBox(height: 24),
            _SecHead('🏠 Roof Color'),
            const SizedBox(height: 12),
            GestureDetector(
              onTap: () => _pickColor(false),
              child: Row(
                children: [
                  Container(
                    width: 48, height: 48,
                    decoration: BoxDecoration(
                      color: _roofColor,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: AppTheme.gold),
                    ),
                  ),
                  const SizedBox(width: 14),
                  Text(_hexColor(_roofColor),
                      style: const TextStyle(
                          color: AppTheme.gold, fontWeight: FontWeight.w600)),
                  const SizedBox(width: 8),
                  const Icon(Icons.edit, color: AppTheme.grey, size: 16),
                ],
              ),
            ),
            const SizedBox(height: 24),
            _SecHead('🏗 Roof Type'),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8, runSpacing: 8,
              children: _roofTypes
                  .map((r) => ChoiceChip(
                        label: Text(r),
                        selected: _roofType == r,
                        onSelected: (_) => setState(() => _roofType = r),
                      ))
                  .toList(),
            ),
            const SizedBox(height: 24),
            _SecHead('🧱 Facade Material'),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8, runSpacing: 8,
              children: _materials
                  .map((m) => ChoiceChip(
                        label: Text(m),
                        selected: _material == m,
                        onSelected: (_) => setState(() => _material = m),
                      ))
                  .toList(),
            ),
            const SizedBox(height: 24),
            _SecHead('🪟 Window Type'),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8, runSpacing: 8,
              children: _windowTypes
                  .map((w) => ChoiceChip(
                        label: Text(w),
                        selected: _windowType == w,
                        onSelected: (_) => setState(() => _windowType = w),
                      ))
                  .toList(),
            ),
            const SizedBox(height: 40),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _loading ? null : _applyCustomization,
                child: _loading
                    ? const SizedBox(
                        height: 20, width: 20,
                        child: CircularProgressIndicator(
                            color: AppTheme.black, strokeWidth: 2))
                    : const Text('Apply & Re-render'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SecHead extends StatelessWidget {
  const _SecHead(this.text);
  final String text;

  @override
  Widget build(BuildContext context) => Text(
        text,
        style: const TextStyle(
            fontSize: 15,
            fontWeight: FontWeight.w700,
            color: AppTheme.white),
      );
}
