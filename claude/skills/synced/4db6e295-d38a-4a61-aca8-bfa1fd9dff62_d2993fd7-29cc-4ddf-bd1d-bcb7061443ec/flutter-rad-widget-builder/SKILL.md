---
name: flutter-rad-widget-builder
description: Generate Flutter widgets following RAD (Reinaldo App Development) standards. Use when creating new StatefulWidgets with RAD prefix, mixins, mode-based layouts, and standardized parameter patterns. Triggers on requests like "create a RAD widget", "build a new input field", "generate a dropdown widget", or any Flutter widget creation for the flutter_rad project.
---

# Flutter RAD Widget Builder

Generate Flutter StatefulWidgets following RAD coding standards.

## Naming Conventions

- Widget class: `RAD{WidgetName}` (e.g., `RADInputField`, `RADComboBox`)
- State class: `RAD{WidgetName}State`
- GlobalKey: `GlobalKey<RAD{WidgetName}State>? globalKey`

## Required Imports

```dart
import 'package:flutter/material.dart';
import 'package:flutter_rad/helper/helper.dart';
import 'package:flutter_rad/helper/mixin_helper.dart';
import 'package:flutter_rad/value/constant.dart';
import 'package:responsive_sizer/responsive_sizer.dart';
```

## Widget Structure Template

```dart
class RAD{WidgetName} extends StatefulWidget {
  // Required callback first (if any)
  final Function({params}) onCallback;
  
  // Common parameters
  final String labelDescription;
  final bool isVisible;
  final String mode;
  final double height;
  final double? width;
  final double? headerWidth;
  final double? valueWidth;
  final double fontSize;
  final double hFontSize;
  final GlobalKey<RAD{WidgetName}State>? globalKey;

  const RAD{WidgetName}({
    required this.onCallback,
    this.labelDescription = "",
    this.isVisible = true,
    this.mode = "0",
    required this.height,
    this.width,
    this.headerWidth,
    this.valueWidth,
    this.fontSize = 12,
    this.hFontSize = 12,
    this.globalKey,
  }) : super(key: globalKey);

  @override
  State<RAD{WidgetName}> createState() => RAD{WidgetName}State();
}
```

## State Class Template

```dart
class RAD{WidgetName}State extends State<RAD{WidgetName}>
    with VisibilityMixin, ErrorMixin {
  
  double? _height;
  late ColorScheme _colorScheme;

  @override
  void initState() {
    super.initState();
    isVisible = widget.isVisible;
    _height = widget.height.minInput; // or .minCombo for dropdowns
  }

  @override
  void didUpdateWidget(RAD{WidgetName} oldWidget) {
    super.didUpdateWidget(oldWidget);
    // Sync props as needed
  }

  @override
  void dispose() {
    // Cleanup listeners/controllers
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    _colorScheme = Theme.of(context).colorScheme;
    return animateVisible(child: buildWidget());
  }

  Widget buildWidget() {
    switch (widget.mode) {
      case "1":
      case "filter":
        return generateFieldWithBorderV2();
      case "2":
        return generateFieldWithBorderV3();
      default:
        return generateFieldWithBorder();
    }
  }

  // Public methods for external control via GlobalKey
  void fieldRequestFocus() {
    Scrollable.ensureVisible(context,
        curve: Curves.elasticIn,
        duration: const Duration(milliseconds: 200),
        alignmentPolicy: ScrollPositionAlignmentPolicy.keepVisibleAtEnd);
  }

  void fieldUpdateValue(dynamic value) {
    setState(() {
      // Update internal state
    });
  }
}
```

## Error Handling

Use `ErrorMixin` which provides:
- `errorMessage` - String? for error text
- Display via `RADTooltipFloating(error: errorMessage!, fontSize: widget.fontSize)`

## Constants Reference

From `constant.dart`:
- `curveRadius` - Border radius
- `defaultPadding` - Standard padding
- `textFieldHorizontalPadding` - Input horizontal padding
- `numeral`, `float`, `thousandSeparator` - Number type lists

## Extensions

From `responsive_sizer`:
- `.sw` - Screen width percentage
- `.minInput` - Minimum input height
- `.minCombo` - Minimum combo box height
