import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../core/theme/app_theme.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final PageController _ctrl = PageController();
  int _page = 0;

  static const _pages = [
    _OBPage(
      icon: Icons.photo_camera_outlined,
      title: 'Describe Your Dream',
      subtitle:
          'Enter your plot dimensions, room needs, and style preference in plain language.',
    ),
    _OBPage(
      icon: Icons.auto_fix_high_outlined,
      title: 'AI Designs It',
      subtitle:
          'Gemini 2.5 Flash crafts a complete building spec — rooms, materials, proportions.',
    ),
    _OBPage(
      icon: Icons.view_in_ar_outlined,
      title: 'See It in 3D',
      subtitle:
          'Blender renders a photorealistic exterior at 1920×1080. Explore in AR on your phone.',
    ),
    _OBPage(
      icon: Icons.download_outlined,
      title: 'Download Everything',
      subtitle:
          'Get your 2D floor plan PNG, 3D render, GLB model, and STL for 3D printing — free.',
    ),
  ];

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  void _next() {
    if (_page < _pages.length - 1) {
      _ctrl.nextPage(
          duration: const Duration(milliseconds: 350), curve: Curves.easeOut);
    } else {
      context.go('/input');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.black,
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: PageView.builder(
                controller: _ctrl,
                itemCount: _pages.length,
                onPageChanged: (i) => setState(() => _page = i),
                itemBuilder: (_, i) => _pages[i],
              ),
            ),
            _Dots(count: _pages.length, current: _page),
            const SizedBox(height: 20),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 32),
              child: SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _next,
                  child:
                      Text(_page == _pages.length - 1 ? 'Get Started' : 'Next'),
                ),
              ),
            ),
            if (_page < _pages.length - 1)
              TextButton(
                onPressed: () => context.go('/input'),
                child: const Text('Skip',
                    style: TextStyle(color: AppTheme.greyLight)),
              ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }
}

class _OBPage extends StatelessWidget {
  const _OBPage({
    required this.icon,
    required this.title,
    required this.subtitle,
  });

  final IconData icon;
  final String title;
  final String subtitle;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(40),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 110,
            height: 110,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(color: AppTheme.gold, width: 1.5),
              color: AppTheme.cardColor,
            ),
            child: Icon(icon, size: 52, color: AppTheme.gold),
          ),
          const SizedBox(height: 40),
          ShaderMask(
            shaderCallback: (r) => kGoldGradient.createShader(r),
            child: Text(
              title,
              style: const TextStyle(
                  fontSize: 28, fontWeight: FontWeight.w800, color: Colors.white),
              textAlign: TextAlign.center,
            ),
          ),
          const SizedBox(height: 16),
          Text(
            subtitle,
            style: const TextStyle(
                fontSize: 15, color: AppTheme.greyLight, height: 1.6),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}

class _Dots extends StatelessWidget {
  const _Dots({required this.count, required this.current});
  final int count;
  final int current;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: List.generate(count, (i) {
        final active = i == current;
        return AnimatedContainer(
          duration: const Duration(milliseconds: 250),
          margin: const EdgeInsets.symmetric(horizontal: 4),
          width: active ? 24 : 8,
          height: 8,
          decoration: BoxDecoration(
            color: active ? AppTheme.gold : AppTheme.grey,
            borderRadius: BorderRadius.circular(4),
          ),
        );
      }),
    );
  }
}
