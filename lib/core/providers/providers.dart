import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/api_models.dart';
import '../services/api_service.dart';
import '../services/generation_service.dart';

// ── API Service ───────────────────────────────────────────────────────────────

final apiServiceProvider = Provider<ApiService>((_) => ApiService());

// ── Generation Service ────────────────────────────────────────────────────────

final generationServiceProvider = Provider<GenerationService>(
  (ref) => GenerationService(ref.read(apiServiceProvider)),
);

// ── Design Input State ────────────────────────────────────────────────────────

class DesignInput {
  final PlotSpec? plot;
  final RoomRequirements? rooms;
  final String style;
  final String budget;
  final String region;
  final String description;
  final String? sitePhotoKey;
  final String? stylePhotoKey;
  final String? sitePhotoPath;  // local file path for preview
  final String? stylePhotoPath;

  const DesignInput({
    this.plot,
    this.rooms,
    this.style = 'modern',
    this.budget = 'medium',
    this.region = 'south_asian',
    this.description = '',
    this.sitePhotoKey,
    this.stylePhotoKey,
    this.sitePhotoPath,
    this.stylePhotoPath,
  });

  DesignInput copyWith({
    PlotSpec? plot,
    RoomRequirements? rooms,
    String? style,
    String? budget,
    String? region,
    String? description,
    String? sitePhotoKey,
    String? stylePhotoKey,
    String? sitePhotoPath,
    String? stylePhotoPath,
  }) =>
      DesignInput(
        plot: plot ?? this.plot,
        rooms: rooms ?? this.rooms,
        style: style ?? this.style,
        budget: budget ?? this.budget,
        region: region ?? this.region,
        description: description ?? this.description,
        sitePhotoKey: sitePhotoKey ?? this.sitePhotoKey,
        stylePhotoKey: stylePhotoKey ?? this.stylePhotoKey,
        sitePhotoPath: sitePhotoPath ?? this.sitePhotoPath,
        stylePhotoPath: stylePhotoPath ?? this.stylePhotoPath,
      );

  GenerateRequest? toRequest() {
    if (plot == null || rooms == null) return null;
    return GenerateRequest(
      plot: plot!,
      rooms: rooms!,
      preferredStyle: style,
      budget: budget,
      region: region,
      description: description.isEmpty ? null : description,
      sitePhotoKey: sitePhotoKey,
      stylePhotoKey: stylePhotoKey,
    );
  }
}

class DesignInputNotifier extends StateNotifier<DesignInput> {
  DesignInputNotifier() : super(const DesignInput());

  void setPlot(PlotSpec p) => state = state.copyWith(plot: p);
  void setRooms(RoomRequirements r) => state = state.copyWith(rooms: r);
  void setStyle(String s) => state = state.copyWith(style: s);
  void setBudget(String b) => state = state.copyWith(budget: b);
  void setRegion(String r) => state = state.copyWith(region: r);
  void setDescription(String d) => state = state.copyWith(description: d);
  void setSitePhoto(String key, String path) =>
      state = state.copyWith(sitePhotoKey: key, sitePhotoPath: path);
  void setStylePhoto(String key, String path) =>
      state = state.copyWith(stylePhotoKey: key, stylePhotoPath: path);
  void reset() => state = const DesignInput();
}

final designInputProvider =
    StateNotifierProvider<DesignInputNotifier, DesignInput>(
  (_) => DesignInputNotifier(),
);

// ── Job Status ────────────────────────────────────────────────────────────────

class JobStatusNotifier extends StateNotifier<JobStatus?> {
  JobStatusNotifier() : super(null);

  void update(JobStatus s) => state = s;
  void clear() => state = null;
}

final jobStatusProvider =
    StateNotifierProvider<JobStatusNotifier, JobStatus?>(
  (_) => JobStatusNotifier(),
);
