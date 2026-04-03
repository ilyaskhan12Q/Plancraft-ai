import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/models/api_models.dart';
import '../../core/providers/providers.dart';
import '../../core/theme/app_theme.dart';

class PlotInputScreen extends ConsumerStatefulWidget {
  const PlotInputScreen({super.key});

  @override
  ConsumerState<PlotInputScreen> createState() => _PlotInputScreenState();
}

class _PlotInputScreenState extends ConsumerState<PlotInputScreen> {
  final _lengthCtrl = TextEditingController(text: '12');
  final _widthCtrl = TextEditingController(text: '8');
  final _frontSetbackCtrl = TextEditingController(text: '3');
  final _backSetbackCtrl = TextEditingController(text: '1.5');
  final _sideSetbackCtrl = TextEditingController(text: '1.5');
  int _floors = 2;
  String _unit = 'meters';
  String _orientation = 'north';
  String _plotType = 'standard';

  static const _orientations = ['north', 'south', 'east', 'west'];
  static const _units = ['meters', 'feet'];
  static const _plotTypes = ['standard', 'corner', 'irregular'];

  @override
  void dispose() {
    _lengthCtrl.dispose();
    _widthCtrl.dispose();
    _frontSetbackCtrl.dispose();
    _backSetbackCtrl.dispose();
    _sideSetbackCtrl.dispose();
    super.dispose();
  }

  void _next() {
    final l = double.tryParse(_lengthCtrl.text);
    final w = double.tryParse(_widthCtrl.text);
    final fs = double.tryParse(_frontSetbackCtrl.text) ?? 0;
    final bs = double.tryParse(_backSetbackCtrl.text) ?? 0;
    final ss = double.tryParse(_sideSetbackCtrl.text) ?? 0;

    if (l == null || w == null || l <= 0 || w <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Enter valid dimensions')),
      );
      return;
    }
    ref.read(designInputProvider.notifier).setPlot(PlotSpec(
          length: l,
          width: w,
          unit: _unit,
          floors: _floors,
          orientation: _orientation,
          plotType: _plotType,
          setbacks: Setbacks(
            front: fs,
            back: bs,
            left: ss,
            right: ss,
          ),
        ));
    context.push('/input/rooms');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.black,
      appBar: AppBar(
        title: const Text('Plot Details'),
        leading: const SizedBox.shrink(),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _SectionHeader('📐 Plot Size'),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _InputField(
                    ctrl: _lengthCtrl,
                    label: 'Length',
                    hint: '12',
                    suffix: _unit == 'meters' ? 'm' : 'ft',
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _InputField(
                    ctrl: _widthCtrl,
                    label: 'Width',
                    hint: '8',
                    suffix: _unit == 'meters' ? 'm' : 'ft',
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            _SectionHeader('🏗 Plot Type'),
            const SizedBox(height: 12),
            _ChipRow(
              options: _plotTypes,
              selected: _plotType,
              onSelect: (v) => setState(() => _plotType = v),
            ),
            const SizedBox(height: 24),
            _SectionHeader('📏 Mandatory Setbacks'),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _InputField(
                    ctrl: _frontSetbackCtrl,
                    label: 'Front',
                    hint: '3',
                    suffix: _unit == 'meters' ? 'm' : 'ft',
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _InputField(
                    ctrl: _backSetbackCtrl,
                    label: 'Back',
                    hint: '1.5',
                    suffix: _unit == 'meters' ? 'm' : 'ft',
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _InputField(
                    ctrl: _sideSetbackCtrl,
                    label: 'Sides',
                    hint: '1.5',
                    suffix: _unit == 'meters' ? 'm' : 'ft',
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            _SectionHeader('📏 Unit'),
            const SizedBox(height: 12),
            _ChipRow(
              options: _units,
              selected: _unit,
              onSelect: (v) => setState(() => _unit = v),
            ),
            const SizedBox(height: 24),
            _SectionHeader('🏢 Number of Floors'),
            const SizedBox(height: 12),
            _StepperRow(
              value: _floors,
              min: 1,
              max: 5,
              onChanged: (v) => setState(() => _floors = v),
            ),
            const SizedBox(height: 24),
            _SectionHeader('🧭 Road Facing'),
            const SizedBox(height: 12),
            _ChipRow(
              options: _orientations,
              selected: _orientation,
              onSelect: (v) => setState(() => _orientation = v),
            ),
            const SizedBox(height: 40),
            _GoldButton(label: 'Next: Rooms & Style →', onTap: _next),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────── Rooms Input ──────────────────────────────────────

class RoomsInputScreen extends ConsumerStatefulWidget {
  const RoomsInputScreen({super.key});

  @override
  ConsumerState<RoomsInputScreen> createState() => _RoomsInputScreenState();
}

class _RoomsInputScreenState extends ConsumerState<RoomsInputScreen> {
  int _bedrooms = 3;
  int _bathrooms = 2;
  bool _living = true, _kitchen = true, _dining = false;
  bool _garage = false, _study = false;
  String _style = 'modern';
  String _budget = 'medium';
  final _descCtrl = TextEditingController();

  static const _styles = ['modern', 'traditional', 'minimalist',
      'colonial', 'mediterranean', 'contemporary'];
  static const _budgets = ['low', 'medium', 'high', 'luxury'];

  @override
  void dispose() {
    _descCtrl.dispose();
    super.dispose();
  }

  void _generate() {
    ref.read(designInputProvider.notifier)
      ..setRooms(RoomRequirements(
        bedrooms: _bedrooms,
        bathrooms: _bathrooms,
        livingRoom: _living,
        kitchen: _kitchen,
        dining: _dining,
        garage: _garage,
        study: _study,
      ))
      ..setStyle(_style)
      ..setBudget(_budget)
      ..setDescription(_descCtrl.text);
    context.push('/generating');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.black,
      appBar: AppBar(title: const Text('Rooms & Style')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _SectionHeader('🛏 Bedrooms'),
            const SizedBox(height: 12),
            _StepperRow(
                value: _bedrooms, min: 1, max: 8,
                onChanged: (v) => setState(() => _bedrooms = v)),
            const SizedBox(height: 20),
            _SectionHeader('🚿 Bathrooms'),
            const SizedBox(height: 12),
            _StepperRow(
                value: _bathrooms, min: 1, max: 6,
                onChanged: (v) => setState(() => _bathrooms = v)),
            const SizedBox(height: 20),
            _SectionHeader('🏠 Rooms to Include'),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8, runSpacing: 8,
              children: [
                _ToggleChip('Living Room', _living,
                    (v) => setState(() => _living = v)),
                _ToggleChip('Kitchen', _kitchen,
                    (v) => setState(() => _kitchen = v)),
                _ToggleChip('Dining', _dining,
                    (v) => setState(() => _dining = v)),
                _ToggleChip('Garage', _garage,
                    (v) => setState(() => _garage = v)),
                _ToggleChip('Study', _study,
                    (v) => setState(() => _study = v)),
              ],
            ),
            const SizedBox(height: 24),
            _SectionHeader('🎨 Architectural Style'),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8, runSpacing: 8,
              children: _styles
                  .map((s) => ChoiceChip(
                        label: Text(s),
                        selected: _style == s,
                        onSelected: (_) => setState(() => _style = s),
                      ))
                  .toList(),
            ),
            const SizedBox(height: 24),
            _SectionHeader('💰 Budget'),
            const SizedBox(height: 12),
            _ChipRow(
              options: _budgets,
              selected: _budget,
              onSelect: (v) => setState(() => _budget = v),
            ),
            const SizedBox(height: 24),
            _SectionHeader('📝 Special Notes (optional)'),
            const SizedBox(height: 12),
            TextField(
              controller: _descCtrl,
              maxLines: 3,
              decoration: const InputDecoration(
                hintText:
                    'e.g. Open kitchen, master bedroom facing east, large windows…',
              ),
            ),
            const SizedBox(height: 40),
            _GoldButton(label: '✨ Generate Design', onTap: _generate),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────── Shared Widgets ──────────────────────────────────

class _SectionHeader extends StatelessWidget {
  const _SectionHeader(this.text);
  final String text;

  @override
  Widget build(BuildContext context) => Text(
        text,
        style: const TextStyle(
            fontSize: 15, fontWeight: FontWeight.w700, color: AppTheme.white),
      );
}

class _InputField extends StatelessWidget {
  const _InputField({
    required this.ctrl,
    required this.label,
    required this.hint,
    this.suffix,
  });
  final TextEditingController ctrl;
  final String label, hint;
  final String? suffix;

  @override
  Widget build(BuildContext context) => TextField(
        controller: ctrl,
        keyboardType: TextInputType.number,
        decoration: InputDecoration(
          labelText: label,
          hintText: hint,
          suffixText: suffix,
        ),
      );
}

class _ChipRow extends StatelessWidget {
  const _ChipRow({
    required this.options,
    required this.selected,
    required this.onSelect,
  });
  final List<String> options;
  final String selected;
  final ValueChanged<String> onSelect;

  @override
  Widget build(BuildContext context) => Wrap(
        spacing: 8, runSpacing: 8,
        children: options
            .map((o) => ChoiceChip(
                  label: Text(o),
                  selected: selected == o,
                  onSelected: (_) => onSelect(o),
                ))
            .toList(),
      );
}

class _StepperRow extends StatelessWidget {
  const _StepperRow({
    required this.value,
    required this.min,
    required this.max,
    required this.onChanged,
  });
  final int value, min, max;
  final ValueChanged<int> onChanged;

  @override
  Widget build(BuildContext context) => Row(
        children: [
          _StepBtn(
              icon: Icons.remove,
              onTap: value > min ? () => onChanged(value - 1) : null),
          const SizedBox(width: 20),
          Text('$value',
              style: const TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.w700,
                  color: AppTheme.gold)),
          const SizedBox(width: 20),
          _StepBtn(
              icon: Icons.add,
              onTap: value < max ? () => onChanged(value + 1) : null),
        ],
      );
}

class _StepBtn extends StatelessWidget {
  const _StepBtn({required this.icon, this.onTap});
  final IconData icon;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) => GestureDetector(
        onTap: onTap,
        child: Container(
          width: 38,
          height: 38,
          decoration: BoxDecoration(
            border: Border.all(
                color: onTap != null ? AppTheme.gold : AppTheme.grey),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(icon,
              color: onTap != null ? AppTheme.gold : AppTheme.grey, size: 18),
        ),
      );
}

class _ToggleChip extends StatelessWidget {
  const _ToggleChip(this.label, this.value, this.onChanged);
  final String label;
  final bool value;
  final ValueChanged<bool> onChanged;

  @override
  Widget build(BuildContext context) => FilterChip(
        label: Text(label),
        selected: value,
        onSelected: onChanged,
      );
}

class _GoldButton extends StatelessWidget {
  const _GoldButton({required this.label, required this.onTap});
  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) => SizedBox(
        width: double.infinity,
        child: ElevatedButton(
          onPressed: onTap,
          child: Text(label),
        ),
      );
}
