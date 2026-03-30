import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/providers/providers.dart';
import '../../core/models/api_models.dart';
import '../../core/theme/app_theme.dart';

class GeneratingScreen extends ConsumerStatefulWidget {
  const GeneratingScreen({super.key});

  @override
  ConsumerState<GeneratingScreen> createState() => _GeneratingScreenState();
}

class _GeneratingScreenState extends ConsumerState<GeneratingScreen>
    with TickerProviderStateMixin {
  late AnimationController _pulseController;
  StreamSubscription<JobStatus>? _sub;

  static const _stages = [
    '🔍 Analysing site photos…',
    '🧠 AI designing building spec…',
    '📐 Validating geometry…',
    '🗺 Rendering 2D floor plan…',
    '🎬 Generating 3D scene…',
    '🖥 Rendering (this takes a few minutes)…',
  ];

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
        vsync: this, duration: const Duration(seconds: 2))
      ..repeat(reverse: true);
    _startGeneration();
  }

  void _startGeneration() {
    final input = ref.read(designInputProvider);
    final request = input.toRequest();
    if (request == null) {
      context.go('/input');
      return;
    }
    final genService = ref.read(generationServiceProvider);
    _sub = genService.generate(request).listen(
      (status) {
        ref.read(jobStatusProvider.notifier).update(status);
        if (status.isDone) {
          context.go('/results');
        } else if (status.isFailed) {
          _showError(status.error ?? 'Unknown error');
        }
      },
      onError: (e) => _showError(e.toString()),
    );
  }

  void _showError(String msg) {
    if (!mounted) return;
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: AppTheme.cardColor,
        title: const Text('Generation Failed',
            style: TextStyle(color: AppTheme.error)),
        content: Text(msg,
            style: const TextStyle(color: AppTheme.greyLight)),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              context.go('/input');
            },
            child: const Text('Try Again',
                style: TextStyle(color: AppTheme.gold)),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _sub?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final status = ref.watch(jobStatusProvider);
    final progress = status?.progress ?? 0.0;
    final stage = status?.stage ?? 'Starting…';

    return Scaffold(
      backgroundColor: AppTheme.black,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            children: [
              const Spacer(),
              // Pulsing gold circle
              AnimatedBuilder(
                animation: _pulseController,
                builder: (_, __) {
                  final glow = 0.3 + _pulseController.value * 0.5;
                  return Container(
                    width: 120,
                    height: 120,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: AppTheme.cardColor,
                      boxShadow: [
                        BoxShadow(
                          color: AppTheme.gold.withOpacity(glow),
                          blurRadius: 50,
                          spreadRadius: 10,
                        ),
                      ],
                      border: Border.all(color: AppTheme.gold, width: 2),
                    ),
                    child: const Icon(Icons.architecture,
                        color: AppTheme.gold, size: 60),
                  );
                },
              ),
              const SizedBox(height: 40),
              ShaderMask(
                shaderCallback: (r) => kGoldGradient.createShader(r),
                child: const Text(
                  'Designing Your Building…',
                  style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.w700,
                      color: Colors.white),
                  textAlign: TextAlign.center,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                stage,
                style: const TextStyle(
                    fontSize: 14, color: AppTheme.greyLight),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),
              // Progress bar
              ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: LinearProgressIndicator(
                  value: progress,
                  minHeight: 8,
                  backgroundColor: AppTheme.cardColor,
                  valueColor:
                      const AlwaysStoppedAnimation<Color>(AppTheme.gold),
                ),
              ),
              const SizedBox(height: 8),
              Text(
                '${(progress * 100).toInt()}%',
                style: const TextStyle(
                    fontSize: 13,
                    color: AppTheme.gold,
                    fontWeight: FontWeight.w600),
              ),
              const Spacer(),
              // Stage list
              ..._stages
                  .asMap()
                  .entries
                  .map((e) => _StageRow(
                        label: e.value,
                        state: _stageState(e.key, progress),
                      )),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  _StageState _stageState(int index, double progress) {
    final thresholds = [0.05, 0.15, 0.30, 0.40, 0.50, 0.90];
    if (progress >= (index < thresholds.length - 1
        ? thresholds[index + 1]
        : 1.0)) {
      return _StageState.done;
    }
    if (progress >= thresholds[index]) return _StageState.active;
    return _StageState.pending;
  }
}

enum _StageState { pending, active, done }

class _StageRow extends StatelessWidget {
  const _StageRow({required this.label, required this.state});
  final String label;
  final _StageState state;

  @override
  Widget build(BuildContext context) {
    final icon = switch (state) {
      _StageState.done   => Icons.check_circle,
      _StageState.active => Icons.radio_button_checked,
      _StageState.pending => Icons.radio_button_unchecked,
    };
    final color = switch (state) {
      _StageState.done   => AppTheme.success,
      _StageState.active => AppTheme.gold,
      _StageState.pending => AppTheme.grey,
    };
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Icon(icon, color: color, size: 18),
          const SizedBox(width: 12),
          Text(label,
              style: TextStyle(
                  color: state == _StageState.pending
                      ? AppTheme.grey
                      : AppTheme.white,
                  fontSize: 13)),
        ],
      ),
    );
  }
}
