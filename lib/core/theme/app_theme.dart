import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  // ── Palette ──────────────────────────────────────────────────────────────
  static const Color black = Color(0xFF0A0A0A);
  static const Color darkSurface = Color(0xFF141414);
  static const Color cardColor = Color(0xFF1E1E1E);
  static const Color gold = Color(0xFFD4AF37);
  static const Color goldLight = Color(0xFFEDD96A);
  static const Color goldDark = Color(0xFF9A7D0A);
  static const Color white = Color(0xFFF8F8F8);
  static const Color grey = Color(0xFF6B6B6B);
  static const Color greyLight = Color(0xFFAAAAAA);
  static const Color error = Color(0xFFE53935);
  static const Color success = Color(0xFF43A047);

  static ThemeData get dark {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: black,
      colorScheme: const ColorScheme.dark(
        primary: gold,
        onPrimary: black,
        secondary: goldLight,
        onSecondary: black,
        surface: darkSurface,
        onSurface: white,
        error: error,
      ),
      textTheme: GoogleFonts.interTextTheme(ThemeData.dark().textTheme).copyWith(
        displayLarge: GoogleFonts.inter(
          fontSize: 32, fontWeight: FontWeight.w700, color: white, letterSpacing: -0.5,
        ),
        displayMedium: GoogleFonts.inter(
          fontSize: 26, fontWeight: FontWeight.w700, color: white, letterSpacing: -0.5,
        ),
        titleLarge: GoogleFonts.inter(
          fontSize: 20, fontWeight: FontWeight.w600, color: white,
        ),
        titleMedium: GoogleFonts.inter(
          fontSize: 16, fontWeight: FontWeight.w600, color: white,
        ),
        bodyLarge: GoogleFonts.inter(fontSize: 16, color: white),
        bodyMedium: GoogleFonts.inter(fontSize: 14, color: greyLight),
        labelLarge: GoogleFonts.inter(
          fontSize: 14, fontWeight: FontWeight.w600, color: black, letterSpacing: 0.5,
        ),
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: black,
        elevation: 0,
        centerTitle: true,
        iconTheme: const IconThemeData(color: gold),
        titleTextStyle: GoogleFonts.inter(
          fontSize: 18, fontWeight: FontWeight.w700, color: white, letterSpacing: -0.3,
        ),
      ),
      cardTheme: CardThemeData(
        color: cardColor,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: Color(0xFF2A2A2A)),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: gold,
          foregroundColor: black,
          elevation: 0,
          padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 32),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          textStyle: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w700),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: gold,
          side: const BorderSide(color: gold, width: 1.5),
          padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 24),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: cardColor,
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Color(0xFF2A2A2A)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Color(0xFF2A2A2A)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: gold, width: 1.5),
        ),
        labelStyle: GoogleFonts.inter(color: greyLight, fontSize: 13),
        hintStyle: GoogleFonts.inter(color: grey, fontSize: 14),
      ),
      sliderTheme: const SliderThemeData(
        activeTrackColor: gold,
        thumbColor: gold,
        inactiveTrackColor: Color(0xFF2A2A2A),
      ),
      chipTheme: ChipThemeData(
        backgroundColor: cardColor,
        selectedColor: gold,
        labelStyle: GoogleFonts.inter(fontSize: 13),
        side: const BorderSide(color: Color(0xFF2A2A2A)),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      ),
      dividerColor: const Color(0xFF2A2A2A),
      iconTheme: const IconThemeData(color: greyLight),
      progressIndicatorTheme: const ProgressIndicatorThemeData(
        color: gold,
        linearTrackColor: Color(0xFF2A2A2A),
      ),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: darkSurface,
        selectedItemColor: gold,
        unselectedItemColor: grey,
      ),
    );
  }
}

// ── Gold gradient ─────────────────────────────────────────────────────────────
const kGoldGradient = LinearGradient(
  colors: [AppTheme.gold, AppTheme.goldLight],
  begin: Alignment.topLeft,
  end: Alignment.bottomRight,
);

const kDarkCardGradient = LinearGradient(
  colors: [Color(0xFF1E1E1E), Color(0xFF141414)],
  begin: Alignment.topLeft,
  end: Alignment.bottomRight,
);
