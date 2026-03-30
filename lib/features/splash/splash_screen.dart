import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../core/theme/app_theme.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with TickerProviderStateMixin {
  late AnimationController _logoController;
  late AnimationController _progressController;
  late Animation<double> _logoOpacity;
  late Animation<double> _logoScale;

  @override
  void initState() {
    super.initState();
    _logoController = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 1200));
    _progressController = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 2000));

    _logoOpacity = CurvedAnimation(parent: _logoController, curve: Curves.easeIn);
    _logoScale = Tween<double>(begin: 0.6, end: 1.0).animate(
        CurvedAnimation(parent: _logoController, curve: Curves.elasticOut));

    _logoController.forward();
    Future.delayed(const Duration(milliseconds: 400), () {
      _progressController.forward();
    });
    Future.delayed(const Duration(milliseconds: 2800), () {
      if (mounted) context.go('/onboarding');
    });
  }

  @override
  void dispose() {
    _logoController.dispose();
    _progressController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.black,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ScaleTransition(
              scale: _logoScale,
              child: FadeTransition(
                opacity: _logoOpacity,
                child: Column(
                  children: [
                    Container(
                      width: 100,
                      height: 100,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        gradient: const RadialGradient(
                          colors: [AppTheme.gold, AppTheme.goldDark],
                        ),
                        boxShadow: [
                          BoxShadow(
                            color: AppTheme.gold.withOpacity(0.4),
                            blurRadius: 40,
                            spreadRadius: 10,
                          ),
                        ],
                      ),
                      child: const Icon(Icons.architecture,
                          color: AppTheme.black, size: 54),
                    ),
                    const SizedBox(height: 24),
                    ShaderMask(
                      shaderCallback: (r) => kGoldGradient.createShader(r),
                      child: const Text(
                        'AI ARCHITECT',
                        style: TextStyle(
                          fontSize: 28,
                          fontWeight: FontWeight.w800,
                          color: Colors.white,
                          letterSpacing: 6,
                        ),
                      ),
                    ),
                    const SizedBox(height: 6),
                    const Text(
                      'Design your dream, rendered in 3D',
                      style: TextStyle(
                          fontSize: 13,
                          color: AppTheme.greyLight,
                          letterSpacing: 1),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 60),
            SizedBox(
              width: 180,
              child: AnimatedBuilder(
                animation: _progressController,
                builder: (_, __) => ClipRRect(
                  borderRadius: BorderRadius.circular(4),
                  child: LinearProgressIndicator(
                    value: _progressController.value,
                    minHeight: 3,
                    backgroundColor: AppTheme.cardColor,
                    valueColor:
                        const AlwaysStoppedAnimation<Color>(AppTheme.gold),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
