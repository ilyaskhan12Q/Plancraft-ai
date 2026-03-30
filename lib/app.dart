import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'core/theme/app_theme.dart';
import 'features/splash/splash_screen.dart';
import 'features/onboarding/onboarding_screen.dart';
import 'features/input/plot_input_screen.dart';
import 'features/generating/generating_screen.dart';
import 'features/results/results_screen.dart';
import 'features/viewer/viewer_screen.dart';
import 'features/customize/customize_screen.dart';
import 'features/export/export_screen.dart';

class AiArchitectApp extends StatelessWidget {
  const AiArchitectApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'AI Architect',
      theme: AppTheme.dark,
      debugShowCheckedModeBanner: false,
      routerConfig: _router,
    );
  }
}

final _router = GoRouter(
  initialLocation: '/splash',
  routes: [
    GoRoute(path: '/splash',      builder: (_, __) => const SplashScreen()),
    GoRoute(path: '/onboarding',  builder: (_, __) => const OnboardingScreen()),
    GoRoute(path: '/input',       builder: (_, __) => const PlotInputScreen()),
    GoRoute(path: '/input/rooms', builder: (_, __) => const RoomsInputScreen()),
    GoRoute(path: '/generating',  builder: (_, __) => const GeneratingScreen()),
    GoRoute(path: '/results',     builder: (_, __) => const ResultsScreen()),
    GoRoute(
      path: '/viewer',
      builder: (ctx, state) {
        final url = state.extra as String? ?? '';
        return ViewerScreen(modelUrl: url);
      },
    ),
    GoRoute(path: '/customize',   builder: (_, __) => const CustomizeScreen()),
    GoRoute(path: '/export',      builder: (_, __) => const ExportScreen()),
  ],
);
