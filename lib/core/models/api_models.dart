// Core data models for AI Architect Flutter app

// ── Plot ──────────────────────────────────────────────────────────────────────

class PlotSpec {
  final double length;
  final double width;
  final String unit;
  final int floors;
  final String orientation;

  const PlotSpec({
    required this.length,
    required this.width,
    this.unit = 'meters',
    this.floors = 1,
    this.orientation = 'north',
  });

  Map<String, dynamic> toJson() => {
        'length': length,
        'width': width,
        'unit': unit,
        'floors': floors,
        'orientation': orientation,
      };
}

// ── Rooms ─────────────────────────────────────────────────────────────────────

class RoomRequirements {
  final int bedrooms;
  final int bathrooms;
  final bool livingRoom;
  final bool kitchen;
  final bool dining;
  final bool garage;
  final bool study;
  final bool servantQuarter;

  const RoomRequirements({
    this.bedrooms = 3,
    this.bathrooms = 2,
    this.livingRoom = true,
    this.kitchen = true,
    this.dining = false,
    this.garage = false,
    this.study = false,
    this.servantQuarter = false,
  });

  Map<String, dynamic> toJson() => {
        'bedrooms': bedrooms,
        'bathrooms': bathrooms,
        'living_room': livingRoom,
        'kitchen': kitchen,
        'dining': dining,
        'garage': garage,
        'study': study,
        'servant_quarter': servantQuarter,
      };
}

// ── Generate Request ───────────────────────────────────────────────────────────

class GenerateRequest {
  final PlotSpec plot;
  final RoomRequirements rooms;
  final String preferredStyle;
  final String budget;
  final String region;
  final String? description;
  final String? sitePhotoKey;
  final String? stylePhotoKey;

  const GenerateRequest({
    required this.plot,
    required this.rooms,
    this.preferredStyle = 'modern',
    this.budget = 'medium',
    this.region = 'south_asian',
    this.description,
    this.sitePhotoKey,
    this.stylePhotoKey,
  });

  Map<String, dynamic> toJson() => {
        'plot': plot.toJson(),
        'rooms': rooms.toJson(),
        'preferred_style': preferredStyle,
        'budget': budget,
        'region': region,
        if (description != null) 'description': description,
        if (sitePhotoKey != null) 'site_photo_key': sitePhotoKey,
        if (stylePhotoKey != null) 'style_photo_key': stylePhotoKey,
      };
}

// ── Job Status ────────────────────────────────────────────────────────────────

class VariantResult {
  final String variant;
  final String? floorplanUrl;
  final String? renderUrl;
  final String? modelUrl;
  final String? stlUrl;

  const VariantResult({
    required this.variant,
    this.floorplanUrl,
    this.renderUrl,
    this.modelUrl,
    this.stlUrl,
  });

  factory VariantResult.fromJson(Map<String, dynamic> j) => VariantResult(
        variant: j['variant'] as String? ?? 'modern',
        floorplanUrl: j['floorplan_url'] as String?,
        renderUrl: j['render_url'] as String?,
        modelUrl: j['model_url'] as String?,
        stlUrl: j['stl_url'] as String?,
      );
}

class JobStatus {
  final String jobId;
  final String status;
  final double progress;
  final String stage;
  final String? error;
  final List<VariantResult> variants;

  const JobStatus({
    required this.jobId,
    required this.status,
    required this.progress,
    required this.stage,
    this.error,
    this.variants = const [],
  });

  factory JobStatus.fromJson(Map<String, dynamic> j) => JobStatus(
        jobId: j['job_id'] as String? ?? '',
        status: j['status'] as String? ?? 'pending',
        progress: (j['progress'] as num?)?.toDouble() ?? 0.0,
        stage: j['stage'] as String? ?? '',
        error: j['error'] as String?,
        variants: (j['variants'] as List<dynamic>? ?? [])
            .map((v) => VariantResult.fromJson(v as Map<String, dynamic>))
            .toList(),
      );

  bool get isDone => status == 'done';
  bool get isFailed => status == 'failed';
  bool get isRunning => status == 'running' || status == 'pending';
}

// ── Export Links ──────────────────────────────────────────────────────────────

class ExportLinks {
  final String jobId;
  final String? floorplan;
  final String? render;
  final String? model;
  final String? stl;

  const ExportLinks({
    required this.jobId,
    this.floorplan,
    this.render,
    this.model,
    this.stl,
  });

  factory ExportLinks.fromJson(Map<String, dynamic> j) => ExportLinks(
        jobId: j['job_id'] as String? ?? '',
        floorplan: j['floorplan'] as String?,
        render: j['render'] as String?,
        model: j['model'] as String?,
        stl: j['stl'] as String?,
      );
}

// ── Customize Request ─────────────────────────────────────────────────────────

class CustomizeRequest {
  final String? exteriorColor;
  final String? roofColor;
  final String? roofType;
  final String? facadeMaterial;
  final String? windowType;

  const CustomizeRequest({
    this.exteriorColor,
    this.roofColor,
    this.roofType,
    this.facadeMaterial,
    this.windowType,
  });

  Map<String, dynamic> toJson() => {
        if (exteriorColor != null) 'exterior_color': exteriorColor,
        if (roofColor != null) 'roof_color': roofColor,
        if (roofType != null) 'roof_type': roofType,
        if (facadeMaterial != null) 'facade_material': facadeMaterial,
        if (windowType != null) 'window_type': windowType,
      };
}
