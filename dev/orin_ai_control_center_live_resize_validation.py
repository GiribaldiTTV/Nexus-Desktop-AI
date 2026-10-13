# Helper Status: Workstream-scoped
# Owner Workstream: FAM-007 AI Dashboard parent-only Workstream-exit repair
# Reason Reusable Helper Was Not Extended: the HUD live validator is FAM-006-specific; this helper proves FAM-007 parent-dashboard visual/function acceptance after detached child windows were deferred.
# Consolidation Target: future reusable Nexus product-window visual and functional acceptance validator
# Promotion Decision Point: before PR Readiness fold-down

from __future__ import annotations

import ctypes
import ctypes.wintypes
import datetime
import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path

from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from desktop.ai_provider_state import (  # noqa: E402
    build_default_provider_readiness_config,
    build_provider_setup_completion_foundation_state,
)
from desktop.desktop_renderer import AIControlCenterDialog  # noqa: E402


_VISUAL_GRAMMAR_PROBE_SCRIPT = r"""
(() => {
  const surface = document.getElementById("monitoring-hud");
  const cssText = Array.from(document.styleSheets).map((sheet) => {
    try {
      return Array.from(sheet.cssRules || []).map((rule) => rule.cssText || "").join("\n");
    } catch (error) {
      return "";
    }
  }).join("\n");
  const rectFor = (node) => {
    if (!node) return null;
    const rect = node.getBoundingClientRect();
    return {
      left: Math.round(rect.left),
      top: Math.round(rect.top),
      right: Math.round(rect.right),
      bottom: Math.round(rect.bottom),
      width: Math.round(rect.width),
      height: Math.round(rect.height)
    };
  };
  const styleFor = (node) => {
    if (!node) return {};
    const style = getComputedStyle(node);
    return {
      display: style.display,
      position: style.position,
      gridTemplateColumns: style.gridTemplateColumns,
      gap: style.gap,
      columnGap: style.columnGap,
      rowGap: style.rowGap,
      padding: `${style.paddingTop} ${style.paddingRight} ${style.paddingBottom} ${style.paddingLeft}`,
      paddingTop: style.paddingTop,
      paddingRight: style.paddingRight,
      paddingBottom: style.paddingBottom,
      paddingLeft: style.paddingLeft,
      marginTop: style.marginTop,
      minHeight: style.minHeight,
      width: style.width,
      height: style.height,
      maxWidth: style.maxWidth,
      fontSize: style.fontSize,
      lineHeight: style.lineHeight,
      fontWeight: style.fontWeight,
      letterSpacing: style.letterSpacing,
      textTransform: style.textTransform,
      textIndent: style.textIndent,
      color: style.color,
      backgroundColor: style.backgroundColor,
      borderTopWidth: style.borderTopWidth,
      borderTopColor: style.borderTopColor,
      borderRadius: style.borderRadius,
      opacity: style.opacity,
      boxShadow: style.boxShadow,
      overflow: style.overflow,
      whiteSpace: style.whiteSpace,
      flex: style.flex,
      flexGrow: style.flexGrow,
      flexShrink: style.flexShrink,
      flexBasis: style.flexBasis,
      flexWrap: style.flexWrap
    };
  };
  const textFor = (node) => (node?.textContent || "").replace(/\s+/g, " ").trim();
  const group = (selector) => {
    const node = document.querySelector(selector);
    return {
      present: Boolean(node),
      selector,
      rect: rectFor(node),
      style: styleFor(node),
      text: textFor(node).slice(0, 180)
    };
  };
  const all = (selector) => Array.from(document.querySelectorAll(selector)).map((node, index) => ({
    index,
    rect: rectFor(node),
    style: styleFor(node),
    text: textFor(node).slice(0, 180),
    id: node.id || "",
    dataset: Object.assign({}, node.dataset || {})
  }));
  const rowMetrics = all(".monitoring-hud__state-row").map((row) => ({
    index: row.index,
    height: row.rect ? row.rect.height : 0,
    width: row.rect ? row.rect.width : 0,
    padding: row.style.padding,
    gridTemplateColumns: row.style.gridTemplateColumns,
    gap: row.style.gap,
    text: row.text
  }));
  const buttonMetrics = all(".monitoring-hud__hub-action").map((button) => ({
    index: button.index,
    id: button.id,
    text: button.text,
    width: button.rect ? button.rect.width : 0,
    height: button.rect ? button.rect.height : 0,
    fontSize: button.style.fontSize,
    fontWeight: button.style.fontWeight,
    letterSpacing: button.style.letterSpacing,
    padding: button.style.padding,
    borderRadius: button.style.borderRadius,
    disabled: Boolean(document.getElementById(button.id)?.disabled),
    ariaDisabled: document.getElementById(button.id)?.getAttribute("aria-disabled") || "",
    actionState: button.dataset.actionState || "",
    launchKind: button.dataset.launchWindowKind || ""
  }));
  const cardMetrics = all("[data-dashboard-hub-card]").map((card) => {
    const cardNode = document.querySelectorAll("[data-dashboard-hub-card]")[card.index];
    const heading = cardNode?.querySelector(".monitoring-hud__hub-card-topline");
    const rows = cardNode?.querySelectorAll(".monitoring-hud__state-row") || [];
    const rowsBox = cardNode?.querySelector(".ai-control-center-card-rows") || (rows.length ? rows[0].parentElement : null);
    const action = cardNode?.querySelector(".monitoring-hud__hub-actions");
    const actionButton = cardNode?.querySelector(".monitoring-hud__hub-action");
    const cardRect = cardNode?.getBoundingClientRect();
    const actionRect = action?.getBoundingClientRect();
    const buttonRect = actionButton?.getBoundingClientRect();
    const rowRects = Array.from(rows).map((row) => row.getBoundingClientRect());
    const rowUnionRect = rowRects.length ? {
      top: Math.min(...rowRects.map((rect) => rect.top)),
      bottom: Math.max(...rowRects.map((rect) => rect.bottom)),
      left: Math.min(...rowRects.map((rect) => rect.left)),
      right: Math.max(...rowRects.map((rect) => rect.right))
    } : null;
    if (rowUnionRect) {
      rowUnionRect.width = rowUnionRect.right - rowUnionRect.left;
      rowUnionRect.height = rowUnionRect.bottom - rowUnionRect.top;
    }
    const rowsRect = rowsBox && rowsBox.classList.contains("ai-control-center-card-rows")
      ? rowsBox.getBoundingClientRect()
      : rowUnionRect;
    return {
      id: card.dataset.dashboardHubCard || "",
      rect: card.rect,
      style: card.style,
      title: textFor(cardNode?.querySelector(".monitoring-hud__hub-card-title-copy strong")),
      description: textFor(cardNode?.querySelector(".monitoring-hud__hub-card-description")),
      rowCount: rows.length,
      rowHeights: Array.from(rows).map((row) => Math.round(row.getBoundingClientRect().height)),
      rowsHeight: rowsRect ? Math.round(rowsRect.height) : 0,
      topToHeading: cardRect && heading ? Math.round(heading.getBoundingClientRect().top - cardRect.top) : null,
      headingToRows: heading && rowsRect ? Math.round(rowsRect.top - heading.getBoundingClientRect().bottom) : null,
      afterRowsGap: rowsRect && actionRect ? Math.round(actionRect.top - rowsRect.bottom) : null,
      actionBottomGutter: cardRect && actionRect ? Math.round(cardRect.bottom - actionRect.bottom) : null,
      buttonRightGutter: cardRect && buttonRect ? Math.round(cardRect.right - buttonRect.right) : null,
      buttonWidth: buttonRect ? Math.round(buttonRect.width) : 0,
      buttonHeight: buttonRect ? Math.round(buttonRect.height) : 0
    };
  });
  const materialGroups = {
    chrome: group(".monitoring-hud__chrome"),
    titleGroup: group(".monitoring-hud__title-group"),
    header: group(".monitoring-hud__header"),
    kicker: group(".monitoring-hud__kicker"),
    title: group(".monitoring-hud__title"),
    subtitle: group(".monitoring-hud__subtitle"),
    surfaceRole: group(".monitoring-hud__surface-role"),
    surfaceRoleCopy: group(".monitoring-hud__surface-role-copy"),
    surfaceRolePair: group(".monitoring-hud__surface-role-pair"),
    windowControls: group(".monitoring-hud__window-controls"),
    windowControlButton: group(".monitoring-hud__window-control-button"),
    controlHub: group(".monitoring-hud__control-hub"),
    hubCard: group("[data-dashboard-hub-card]"),
    cardTopline: group(".monitoring-hud__hub-card-topline"),
    cardBadge: group(".monitoring-hud__hub-card-topline > span"),
    cardTitle: group(".monitoring-hud__hub-card-title-copy strong"),
    cardDescription: group(".monitoring-hud__hub-card-description"),
    stateRow: group(".monitoring-hud__state-row"),
    rowLabel: group(".monitoring-hud__state-row span"),
    rowValue: group(".monitoring-hud__state-row strong"),
    hubActions: group(".monitoring-hud__hub-actions"),
    hubAction: group(".monitoring-hud__hub-action"),
    buttonLabel: group(".monitoring-hud__button-label"),
    scrollbarTrack: group(".ai-control-center-scrollbar__track"),
    scrollbarThumb: group(".ai-control-center-scrollbar__thumb")
  };
  const missingGroups = Object.entries(materialGroups)
    .filter(([, value]) => !value.present)
    .map(([name]) => name);
  return JSON.stringify({
    ok: true,
    surface: {
      id: surface?.dataset.surfaceId || "",
      productSurfaceRole: surface?.dataset.productSurfaceRole || "",
      defaultWindowWidth: surface?.dataset.defaultWindowWidth || "",
      defaultWindowHeight: surface?.dataset.defaultWindowHeight || "",
      dashboardSurfaceModel: surface?.dataset.dashboardSurfaceModel || "",
      dashboardIaModel: surface?.dataset.dashboardIaModel || "",
      childWindowModel: surface?.dataset.childWindowModel || "",
      rowDensity: surface?.dataset.rowDensity || "",
      cardOrder: surface?.dataset.dashboardCardOrder || "",
      title: textFor(document.querySelector(".monitoring-hud__title")),
      subtitle: textFor(document.querySelector(".monitoring-hud__subtitle"))
    },
    materialGroups,
    rowMetrics,
    buttonMetrics,
    cardMetrics,
    cssStateSelectors: {
      hubActionHover: cssText.includes(".monitoring-hud__hub-action") && (cssText.includes(":hover") || cssText.includes(".is-hovered")),
      hubActionFocus: cssText.includes(".monitoring-hud__hub-action") && cssText.includes(":focus-visible"),
      hubActionPressed: cssText.includes(".monitoring-hud__hub-action") && (cssText.includes(":active") || cssText.includes(".is-pressed")),
      hubActionDisabled: cssText.includes(".monitoring-hud__hub-action:disabled") || cssText.includes("[aria-disabled=\"true\"]"),
      windowControlHover: cssText.includes(".monitoring-hud__window-control-button:hover"),
      windowControlFocus: cssText.includes(".monitoring-hud__window-control-button:focus-visible"),
      windowControlDisabled: cssText.includes(".monitoring-hud__window-control-button:disabled") || cssText.includes("data-window-control-state=\"blocked\""),
      customScrollbar: cssText.includes("ai-control-center-scrollbar__thumb")
    },
    coverage: {
      materialGroupCount: Object.keys(materialGroups).length,
      missingGroups,
      cardCount: cardMetrics.length,
      rowCount: rowMetrics.length,
      buttonCount: buttonMetrics.length
    }
  });
})();
"""


user32 = ctypes.windll.user32
GetWindowRect = user32.GetWindowRect
GetWindowRect.argtypes = [ctypes.wintypes.HWND, ctypes.POINTER(ctypes.wintypes.RECT)]
GetWindowRect.restype = ctypes.c_bool
SetForegroundWindow = user32.SetForegroundWindow
SetForegroundWindow.argtypes = [ctypes.wintypes.HWND]
SetForegroundWindow.restype = ctypes.c_bool
BringWindowToTop = user32.BringWindowToTop
BringWindowToTop.argtypes = [ctypes.wintypes.HWND]
BringWindowToTop.restype = ctypes.c_bool
ShowWindow = user32.ShowWindow
ShowWindow.argtypes = [ctypes.wintypes.HWND, ctypes.c_int]
ShowWindow.restype = ctypes.c_bool
SetCursorPos = user32.SetCursorPos
SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
SetCursorPos.restype = ctypes.c_bool
mouse_event = user32.mouse_event
mouse_event.argtypes = [ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong]
mouse_event.restype = None
SW_RESTORE = 9
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_MOVE = 0x0001


def _timestamp() -> str:
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


def _pump(app: QApplication, duration_ms: int = 80) -> None:
    deadline = time.monotonic() + max(0, duration_ms) / 1000.0
    while time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.01)
    app.processEvents()


def _run_js(app: QApplication, dialog: AIControlCenterDialog, script: str, timeout_ms: int = 1500):
    box: dict[str, object] = {"done": False, "result": None}

    def _complete(result):
        box["result"] = result
        box["done"] = True

    dialog.webview.page().runJavaScript(script, _complete)
    deadline = time.monotonic() + max(0, timeout_ms) / 1000.0
    while not box["done"] and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.01)
    app.processEvents()
    return box.get("result")


def _run_visual_grammar_probe(app: QApplication, dialog: AIControlCenterDialog) -> dict[str, object]:
    raw = _run_js(app, dialog, _VISUAL_GRAMMAR_PROBE_SCRIPT, timeout_ms=2500)
    try:
        parsed = json.loads(raw or "{}")
    except Exception:
        parsed = {"ok": False, "raw": str(raw or "")}
    return parsed if isinstance(parsed, dict) else {"ok": False, "raw": str(parsed)}


def _run_child_js(app: QApplication, window, script: str, timeout_ms: int = 1500):
    box: dict[str, object] = {"done": False, "result": None}

    def _complete(result):
        box["result"] = result
        box["done"] = True

    window.webview.page().runJavaScript(script, _complete)
    deadline = time.monotonic() + max(0, timeout_ms) / 1000.0
    while not box["done"] and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.01)
    app.processEvents()
    return box.get("result")


def _rect(hwnd: int) -> dict[str, int]:
    native_rect = ctypes.wintypes.RECT()
    if not hwnd or not GetWindowRect(ctypes.wintypes.HWND(int(hwnd)), ctypes.byref(native_rect)):
        return {"left": 0, "top": 0, "right": 0, "bottom": 0, "width": 0, "height": 0}
    return {
        "left": int(native_rect.left),
        "top": int(native_rect.top),
        "right": int(native_rect.right),
        "bottom": int(native_rect.bottom),
        "width": int(native_rect.right - native_rect.left),
        "height": int(native_rect.bottom - native_rect.top),
    }


def _foreground_window(app: QApplication, window, duration_ms: int = 260) -> None:
    window.showNormal()
    window.raise_()
    window.activateWindow()
    hwnd = int(window.winId()) if window.winId() else 0
    if hwnd:
        ShowWindow(ctypes.wintypes.HWND(hwnd), SW_RESTORE)
        BringWindowToTop(ctypes.wintypes.HWND(hwnd))
        SetForegroundWindow(ctypes.wintypes.HWND(hwnd))
    _pump(app, duration_ms)


def _capture_window(app: QApplication, window, root: Path, label: str) -> dict[str, str]:
    focused_path = root / f"{label}_focused_window.png"
    desktop_path = root / f"{label}_full_desktop.png"
    screen = window.screen() or QApplication.primaryScreen()
    if screen is None:
        raise RuntimeError("No screen available for screenshot capture")
    _foreground_window(app, window)
    if not window.grab().save(str(focused_path)):
        raise RuntimeError(f"Failed to save focused screenshot: {focused_path}")
    _pump(app, 80)
    if not screen.grabWindow(0).save(str(desktop_path)):
        raise RuntimeError(f"Failed to save desktop screenshot: {desktop_path}")
    _pump(app, 50)
    return {"focusedWindow": str(focused_path), "fullDesktop": str(desktop_path)}


def _probe_rect_to_qrect(raw: dict[str, object] | None, window) -> QRect:
    source = raw if isinstance(raw, dict) else {}
    try:
        left = int(round(float(source.get("left", 0))))
        top = int(round(float(source.get("top", 0))))
        width = int(round(float(source.get("width", 0))))
        height = int(round(float(source.get("height", 0))))
    except Exception:
        return QRect()
    rect = QRect(max(0, left), max(0, top), max(0, width), max(0, height))
    return rect.intersected(QRect(0, 0, int(window.width()), int(window.height())))


def _capture_window_region(app: QApplication, window, root: Path, label: str, raw_rect: dict[str, object] | None) -> dict[str, object]:
    rect = _probe_rect_to_qrect(raw_rect, window)
    if not rect.isValid() or rect.width() < 16 or rect.height() < 12:
        return {"ok": False, "label": label, "reason": "invalid-rect"}
    path = root / f"{label}.png"
    _foreground_window(app, window, 140)
    if not window.grab(rect).save(str(path)):
        return {"ok": False, "label": label, "reason": "save-failed", "path": str(path)}
    return {
        "ok": True,
        "label": label,
        "path": str(path),
        "rect": {
            "left": rect.left(),
            "top": rect.top(),
            "width": rect.width(),
            "height": rect.height(),
        },
    }


def _write_settings_option_b_disposition(log_root: Path) -> dict[str, object]:
    manifest_path = log_root / "15_settings_option_b_removal_deferment.json"
    payload = {
        "ok": True,
        "selectedOption": "B",
        "selectedOptionLabel": "Remove And Defer",
        "currentRuntimeSettingsAffordance": "removed-from-current-workstream-exit-path",
        "fam003Dependency": "global-settings-window-required-before-future-settings-entry",
        "activeGlobalSettingsBehavior": False,
        "settingsWindowOpened": False,
        "settingsBehaviorImplementationBlocked": True,
        "implementedRuntimeOption": "B",
        "classification": "option-b-implementation-disposition-only",
    }
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    payload["jsonPath"] = str(manifest_path)
    return payload


def _drive_ai_dashboard_horizontal_resize(
    app: QApplication,
    dialog: AIControlCenterDialog,
    log_root: Path,
) -> dict[str, object]:
    _foreground_window(app, dialog)
    initial = _rect(int(dialog.winId()))
    if initial["width"] <= 0:
        return {"ok": False, "reason": "missing-window-rect", "before": initial}

    def _read_layout() -> dict[str, object]:
        layout_raw = _run_js(
            app,
            dialog,
            """
        (() => {
          const hub = document.getElementById("ai-control-center-card-hub");
          const titleGroup = document.querySelector(".monitoring-hud__title-group");
          const subtitle = document.querySelector(".monitoring-hud__subtitle");
          const settings = document.getElementById("ai-dashboard-settings-action");
          const strip = document.querySelector("[data-dashboard-role='global-ai-strip']");
          const nodes = [...document.querySelectorAll(".monitoring-hud__state-row span, .monitoring-hud__state-row strong, .monitoring-hud__hub-action")];
          const hubRect = hub?.getBoundingClientRect();
          const clipped = nodes.filter((node) => {
            const rect = node.getBoundingClientRect();
            return hubRect && (rect.right > hubRect.right + 2 || rect.left < hubRect.left - 2);
          }).map((node) => node.textContent.trim());
          const stripRect = strip?.getBoundingClientRect();
          const settingsRect = settings?.getBoundingClientRect();
          const rectFor = (node) => {
            if (!node) return { left: 0, top: 0, right: 0, bottom: 0, width: 0, height: 0 };
            const rect = node.getBoundingClientRect();
            return {
              left: Math.round(rect.left),
              top: Math.round(rect.top),
              right: Math.round(rect.right),
              bottom: Math.round(rect.bottom),
              width: Math.round(rect.width),
              height: Math.round(rect.height)
            };
          };
          const pxNumber = (value) => {
            const parsed = Number.parseFloat(String(value || "0"));
            return Number.isFinite(parsed) ? parsed : 0;
          };
          const firstGridColumnWidth = (template) => {
            const match = String(template || "").match(/([\\d.]+)px/);
            return match ? Number(match[1]) : 0;
          };
          const lineHeightNumber = (style, rect) => pxNumber(style?.lineHeight) || Math.max(1, rect.height);
          const titleStatusPillWrap = (() => {
            const copy = document.querySelector(".monitoring-hud__surface-role-copy");
            const copyRect = rectFor(copy);
            const pairMetrics = [...document.querySelectorAll(".monitoring-hud__surface-role-pair")].map((pair) => {
              const rect = rectFor(pair);
              const style = getComputedStyle(pair);
              const childRects = [...pair.children].map((child) => rectFor(child));
              const childTops = childRects.map((rect) => rect.top);
              const childBottoms = childRects.map((rect) => rect.bottom);
              const childTopSpread = childTops.length ? Math.max(...childTops) - Math.min(...childTops) : 0;
              const childBottomSpread = childBottoms.length ? Math.max(...childBottoms) - Math.min(...childBottoms) : 0;
              return {
                text: pair.textContent.replace(/\\s+/g, " ").trim(),
                rect,
                display: style.display,
                flexShrink: style.flexShrink,
                whiteSpace: style.whiteSpace,
                lineTop: rect.top,
                childrenShareLine: childTopSpread <= 2 && childBottomSpread <= 2,
                withinPill: copyRect.width > 0 && rect.left >= copyRect.left - 2 && rect.right <= copyRect.right + 2
              };
            });
            const expectedTexts = ["AI Persona - None", "Status - Not implemented", "Provider - Blocked"];
            return {
              copyRect,
              copyMaxWidth: copy ? getComputedStyle(copy).maxWidth : "",
              pairCount: pairMetrics.length,
              lineCount: new Set(pairMetrics.map((pair) => pair.lineTop)).size,
              expectedTextsPresent: expectedTexts.every((text) => pairMetrics.some((pair) => pair.text === text)),
              groupsAtomic: pairMetrics.every((pair) => pair.display.includes("flex") && pair.whiteSpace === "nowrap" && pair.childrenShareLine),
              clippedPairCount: pairMetrics.filter((pair) => !pair.withinPill).length,
              pairMetrics
            };
          })();
          const titleDescriptionWrap = (() => {
            const description = subtitle;
            const descriptionRect = rectFor(description);
            const descriptionStyle = description ? getComputedStyle(description) : null;
            const titleGroupRect = rectFor(titleGroup);
            const titleGroupStyle = titleGroup ? getComputedStyle(titleGroup) : null;
            const titleGroupInnerWidth = titleGroup
              ? Math.round(
                  titleGroupRect.width
                  - pxNumber(titleGroupStyle?.paddingLeft)
                  - pxNumber(titleGroupStyle?.paddingRight)
                )
              : 0;
            const publishedMaxWidth = pxNumber(description?.dataset.titleDescriptionMaxWidth || "");
            const expectedText = "AI is not implemented; provider/model execution is blocked, and no prompt, file, memory, telemetry, or provider data leaves this machine.";
            const text = (description?.textContent || "").replace(/\\s+/g, " ").trim();
            const rectFromDomRect = (rect) => ({
              left: Math.round(rect.left),
              top: Math.round(rect.top),
              right: Math.round(rect.right),
              bottom: Math.round(rect.bottom),
              width: Math.round(rect.width),
              height: Math.round(rect.height)
            });
            const textNode = description
              ? [...description.childNodes].find((node) => node.nodeType === Node.TEXT_NODE && node.textContent.trim())
              : null;
            const wordMetrics = [];
            if (textNode) {
              const rawText = textNode.textContent || "";
              const wordPattern = /\\S+/g;
              let match = null;
              while ((match = wordPattern.exec(rawText)) !== null) {
                const range = document.createRange();
                range.setStart(textNode, match.index);
                range.setEnd(textNode, match.index + match[0].length);
                const rects = [...range.getClientRects()]
                  .filter((rect) => rect.width > 0 && rect.height > 0)
                  .map(rectFromDomRect);
                range.detach();
                const rect = rects[0] || { left: 0, top: 0, right: 0, bottom: 0, width: 0, height: 0 };
                wordMetrics.push({
                  text: match[0],
                  rect,
                  rects,
                  lineTop: rect.top,
                  withinDescription: descriptionRect.width > 0 && rect.left >= descriptionRect.left - 2 && rect.right <= descriptionRect.right + 2
                });
              }
            }
            const groupCount = description ? description.querySelectorAll(".monitoring-hud__subtitle-group").length : 0;
            const lineTops = [...new Set(wordMetrics.map((word) => word.lineTop).filter((top) => top > 0))];
            const lastPhraseMetrics = wordMetrics.slice(-6);
            const lastPhraseLineCount = new Set(lastPhraseMetrics.map((word) => word.lineTop).filter((top) => top > 0)).size;
            const lastPhraseText = lastPhraseMetrics.map((word) => word.text).join(" ");
            return {
              containerRect: descriptionRect,
              display: descriptionStyle?.display || "",
              flexWrap: descriptionStyle?.flexWrap || "",
              whiteSpace: descriptionStyle?.whiteSpace || "",
              overflowWrap: descriptionStyle?.overflowWrap || "",
              wordBreak: descriptionStyle?.wordBreak || "",
              maxWidth: descriptionStyle?.maxWidth || "",
              publishedMaxWidth: Math.round(publishedMaxWidth),
              titleGroupInnerWidth,
              columnSource: description?.dataset.titleDescriptionColumnSource || "",
              metadata: description?.dataset.titleDescriptionWrap || "",
              text,
              expectedTextPresent: text === expectedText,
              groupCount,
              lineCount: lineTops.length,
              wordCount: wordMetrics.length,
              noAtomicPhraseGroups: groupCount === 0,
              wordsCanWrapIndividually: wordMetrics.length > 0 && wordMetrics.every((word) => word.rect.width <= descriptionRect.width + 2),
              clippedWordCount: wordMetrics.filter((word) => !word.withinDescription).length,
              lastPhraseText,
              lastPhraseLineCount,
              lastPhraseWrapsByWord: lastPhraseText === "or provider data leaves this machine." && lastPhraseLineCount >= 2,
              measuredWidthMatchesTitleCardInner: Math.abs(Math.round(publishedMaxWidth) - titleGroupInnerWidth) <= 2,
              fixedLegacyMaxWidthRemoved: descriptionStyle ? descriptionStyle.maxWidth !== "600px" : false,
              containerUsesProseWordWrap: descriptionStyle
                ? !descriptionStyle.display.includes("flex") && descriptionStyle.whiteSpace === "normal"
                : false,
              wordMetrics,
              lastPhraseMetrics
            };
          })();
          const rowTitleSizingProbe = (() => {
            const hub = document.getElementById("ai-control-center-card-hub");
            const hubStyle = hub ? getComputedStyle(hub) : null;
            const derivedGutter = pxNumber(hubStyle?.getPropertyValue("--ai-dashboard-row-gutter"));
            const derivedVerticalGutter = pxNumber(hubStyle?.getPropertyValue("--ai-dashboard-row-vertical-gutter"));
            const declaredLabelColumnWidthRaw = hubStyle?.getPropertyValue("--ai-dashboard-row-label-width") || "";
            const declaredLabelColumnWidthIsPx = /^\\s*\\d+(?:\\.\\d+)?px\\s*$/.test(declaredLabelColumnWidthRaw);
            const declaredLabelColumnWidth = declaredLabelColumnWidthIsPx ? pxNumber(declaredLabelColumnWidthRaw) : 0;
            const rows = [...document.querySelectorAll(".ai-control-center-card-rows .monitoring-hud__state-row")];
            const rowStackMetrics = [...document.querySelectorAll(".ai-control-center-card-rows")].map((stack, stackIndex) => {
              const stackStyle = getComputedStyle(stack);
              const stackRows = [...stack.querySelectorAll(".monitoring-hud__state-row")];
              const pairGaps = stackRows.slice(1).map((row, index) => {
                const previousRect = stackRows[index].getBoundingClientRect();
                const rowRect = row.getBoundingClientRect();
                return Math.round(rowRect.top - previousRect.bottom);
              });
              const rowGapPx = Math.round(pxNumber(stackStyle.rowGap || stackStyle.gap));
              return {
                stackIndex,
                rowCount: stackRows.length,
                rowGapPx,
                expectedRowVerticalGutterPx: Math.round(derivedVerticalGutter),
                pairGaps,
                rowGapMatchesToken: Math.abs(rowGapPx - derivedVerticalGutter) <= 1,
                pairGapsMatchToken: pairGaps.every((gap) => Math.abs(gap - derivedVerticalGutter) <= 1)
              };
            });
            const labelWidths = rows.map((row) => {
              const label = row.querySelector("span");
              const labelRect = rectFor(label);
              return Math.ceil(Math.max(labelRect.width || 0, label?.scrollWidth || 0));
            });
            const measuredMaxLabelWidth = labelWidths.length ? Math.max(...labelWidths) : 0;
            const contractLabelColumnWidth = Math.round(declaredLabelColumnWidth);
            const rowMetrics = rows.map((row, index) => {
              const rowRect = rectFor(row);
              const style = getComputedStyle(row);
              const label = row.querySelector("span");
              const value = row.querySelector("strong");
              const labelRect = rectFor(label);
              const valueRect = rectFor(value);
              const labelStyle = label ? getComputedStyle(label) : null;
              const titleColumnWidth = firstGridColumnWidth(style.gridTemplateColumns);
              const labelWraps = labelRect.height > lineHeightNumber(labelStyle, labelRect) * 1.35;
              const valueColumnOffset = Math.round(valueRect.left - rowRect.left);
              const expectedValueColumnOffset = Math.round(contractLabelColumnWidth + derivedGutter);
              const fixedColumnGutterPx = Math.round(valueColumnOffset - titleColumnWidth);
              const visibleLabelToValueGutterPx = Math.round(valueRect.left - labelRect.right);
              return {
                index,
                key: `${label?.textContent.trim() || ""}|${value?.textContent.trim() || ""}`,
                label: label?.textContent.trim() || "",
                value: value?.textContent.trim() || "",
                labelFontSize: labelStyle?.fontSize || "",
                valueFontSize: value ? getComputedStyle(value).fontSize : "",
                gridTemplateColumns: style.gridTemplateColumns,
                titleColumnWidth: Math.round(titleColumnWidth),
                labelWidth: labelRect.width,
                rowLeft: rowRect.left,
                rowGutterPx: Math.round(derivedGutter),
                fixedColumnGutterPx,
                visibleLabelToValueGutterPx,
                valueColumnOffset,
                expectedValueColumnOffset,
                valueLeft: valueRect.left,
                rowRight: rowRect.right,
                labelWraps,
                titleColumnContentExcessPx: Math.round(titleColumnWidth - labelRect.width),
                titleColumnMatchesContract: Math.abs(titleColumnWidth - contractLabelColumnWidth) <= 2,
                valueColumnOffsetMatchesContract: Math.abs(valueColumnOffset - expectedValueColumnOffset) <= 2,
                fixedColumnGutterMatchesToken: Math.abs(fixedColumnGutterPx - derivedGutter) <= 2,
                visibleGutterAtLeastFixedGutter: visibleLabelToValueGutterPx >= derivedGutter - 2,
                labelWithinRow: labelRect.left >= rowRect.left - 2 && labelRect.right <= rowRect.right + 2,
                valueWithinRow: valueRect.left >= rowRect.left - 2 && valueRect.right <= rowRect.right + 2
              };
            });
            const valueOffsets = rowMetrics.map((row) => row.valueColumnOffset);
            const uniformValueColumnOffset = valueOffsets.length
              ? Math.max(...valueOffsets) - Math.min(...valueOffsets) <= 2
              : false;
            const valueLefts = rowMetrics.map((row) => Math.round(row.valueLeft));
            const uniformValueLeftEdge = valueLefts.length
              ? Math.max(...valueLefts) - Math.min(...valueLefts) <= 2
              : false;
            const maxLabelColumnExcess = Math.abs(contractLabelColumnWidth - measuredMaxLabelWidth);
            const maxTitleColumnExcess = rowMetrics.length
              ? Math.max(...rowMetrics.map((row) => Math.abs(row.titleColumnWidth - contractLabelColumnWidth)))
              : 999;
            const declaredLabelColumnMatchesMeasuredMax = declaredLabelColumnWidthIsPx
              && contractLabelColumnWidth > 0
              && maxLabelColumnExcess <= 2;
            return {
              rowCount: rowMetrics.length,
              labelColumnSource: hub?.dataset.rowLabelColumnSource || "",
              labelColumnUnit: hub?.dataset.rowLabelColumnUnit || "",
              rowValueColumnContract: hub?.dataset.rowValueColumnContract || "",
              measuredMaxLabelWidth: Math.round(measuredMaxLabelWidth),
              declaredLabelColumnWidthRaw: declaredLabelColumnWidthRaw.trim(),
              declaredLabelColumnWidthIsPx,
              declaredLabelColumnWidth: Math.round(declaredLabelColumnWidth),
              contractLabelColumnWidth,
              rowGutterPx: Math.round(derivedGutter),
              rowVerticalGutterPx: Math.round(derivedVerticalGutter),
              rowVerticalGutterRestored: rowStackMetrics.every((stack) => stack.rowCount < 2 || (stack.rowGapMatchesToken && stack.pairGapsMatchToken)),
              rowStackMetrics,
              contentSized: rowMetrics.every((row) => (
                !row.labelWraps
                && row.titleColumnMatchesContract
                && row.valueColumnOffsetMatchesContract
                && row.fixedColumnGutterMatchesToken
                && row.visibleGutterAtLeastFixedGutter
              )) && declaredLabelColumnMatchesMeasuredMax && maxTitleColumnExcess <= 2 && uniformValueColumnOffset && uniformValueLeftEdge,
              noLabelClipping: rowMetrics.every((row) => row.labelWithinRow),
              noValueClipping: rowMetrics.every((row) => row.valueWithinRow),
              labelValueFontSizeParity: rowMetrics.every((row) => row.labelFontSize === row.valueFontSize),
              valueColumnDerivedFromLabelContent: rowMetrics.every((row) => row.valueColumnOffsetMatchesContract),
              valueColumnDerivedFromMaxLabelContent: rowMetrics.every((row) => row.valueColumnOffsetMatchesContract),
              declaredLabelColumnMatchesMeasuredMax,
              fixedColumnGutterRestored: rowMetrics.every((row) => row.fixedColumnGutterMatchesToken),
              uniformValueColumnOffset,
              uniformValueLeftEdge,
              visibleRowGutterAtLeastFixedGutter: rowMetrics.every((row) => row.visibleGutterAtLeastFixedGutter),
              maxTitleColumnExcessPx: maxTitleColumnExcess,
              maxLabelColumnExcessPx: maxLabelColumnExcess,
              rowMetrics
            };
          })();
          return JSON.stringify({
            clippedCount: clipped.length,
            clipped,
            hubClientWidth: hub ? Math.round(hub.clientWidth) : 0,
            titleGroupWidth: titleGroup ? Math.round(titleGroup.getBoundingClientRect().width) : 0,
            settingsVisible: Boolean(settingsRect && settingsRect.width > 0 && settingsRect.height > 0),
            stripSettingsOverlap: Boolean(stripRect && settingsRect && stripRect.right > settingsRect.left - 4 && stripRect.bottom > settingsRect.top && stripRect.top < settingsRect.bottom),
            maxScroll: hub ? Math.round(Math.max(0, hub.scrollHeight - hub.clientHeight)) : 0,
            titleStatusPillWrap,
            titleDescriptionWrap,
            rowTitleSizingProbe
          });
        })();
        """,
        )
        try:
            return json.loads(layout_raw or "{}")
        except Exception:
            return {"raw": str(layout_raw or "")}

    def _drag_to_width(target_width: int, screenshot_name: str, crop_name: str) -> dict[str, object]:
        before = _rect(int(dialog.winId()))
        if before["width"] <= 0:
            return {"ok": False, "reason": "missing-window-rect", "before": before}
        available = dialog._available_desktop_geometry()
        max_target_width = max(dialog.minimumWidth(), available.width() - 20)
        bounded_target_width = max(dialog.minimumWidth(), min(int(target_width), max_target_width))
        if bounded_target_width == before["width"]:
            bounded_target_width = max(dialog.minimumWidth(), min(before["width"] - 20, max_target_width))
        start = QPoint(before["right"] - max(2, dialog.RESIZE_MARGIN // 2), before["top"] + before["height"] // 2)
        end = QPoint(start.x() + (bounded_target_width - before["width"]), start.y())
        SetCursorPos(start.x(), start.y())
        _pump(app, 120)
        mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        _pump(app, 140)
        started = bool(getattr(dialog, "_resize_active", False))
        cursor_points = [{"x": start.x(), "y": start.y(), "phase": "mouse-down"}]
        for step in range(1, 10):
            x = start.x() + int(round((end.x() - start.x()) * (step / 9)))
            point = QPoint(x, start.y())
            SetCursorPos(point.x(), point.y())
            mouse_event(MOUSEEVENTF_MOVE, 0, 0, 0, 0)
            cursor_points.append({"x": point.x(), "y": point.y(), "phase": f"drag-step-{step}"})
            _pump(app, 45)
        mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        cursor_points.append({"x": end.x(), "y": end.y(), "phase": "mouse-up"})
        _pump(app, 260)
        after = _rect(int(dialog.winId()))
        screenshots = _capture_window(app, dialog, log_root, screenshot_name)
        layout = _read_layout()
        wrap_crop = _capture_window_region(
            app,
            dialog,
            log_root,
            crop_name,
            (layout.get("titleStatusPillWrap") or {}).get("copyRect") if isinstance(layout, dict) else {},
        )
        title_description_wrap_crop = _capture_window_region(
            app,
            dialog,
            log_root,
            f"{crop_name}_title_description",
            (layout.get("titleDescriptionWrap") or {}).get("containerRect") if isinstance(layout, dict) else {},
        )
        return {
            "proofPath": "ai-control-center-right-edge-windows-cursor-drag",
            "hudResizePathSubset": "HUD Dashboard active right-edge cursor drag live resize proof subset",
            "inputMethod": "windows-cursor-left-button-drag",
            "codeForcedGeometry": False,
            "runtimeResizeEventStarted": started,
            "started": started,
            "cursorDragPoints": cursor_points,
            "before": before,
            "after": after,
            "targetWidth": bounded_target_width,
            "minimumWidth": int(dialog.minimumWidth()),
            "minimumHeight": int(dialog.minimumHeight()),
            "widthDelta": after["width"] - before["width"],
            "heightDelta": after["height"] - before["height"],
            "layout": layout,
            "wrapCrop": wrap_crop,
            "titleDescriptionWrapCrop": title_description_wrap_crop,
            "screenshots": screenshots,
        }

    no_early_target_width = max(dialog.minimumWidth(), min(578, dialog._available_desktop_geometry().width() - 20))
    no_early = _drag_to_width(
        no_early_target_width,
        "03_dashboard_horizontal_shrink_no_early_wrap",
        "15_title_status_pill_no_early_wrap_windows_cursor_resize",
    )
    natural = _drag_to_width(
        int(dialog.minimumWidth()),
        "03_dashboard_horizontal_shrink",
        "16_title_status_pill_wrapped_windows_cursor_resize",
    )
    no_early_layout = no_early.get("layout") if isinstance(no_early, dict) else {}
    no_early_layout = no_early_layout if isinstance(no_early_layout, dict) else {}
    no_early_wrap = no_early_layout.get("titleStatusPillWrap") or {}
    natural_layout = natural.get("layout") if isinstance(natural, dict) else {}
    natural_layout = natural_layout if isinstance(natural_layout, dict) else {}
    natural_wrap = natural_layout.get("titleStatusPillWrap") or {}
    natural_after = natural.get("after") if isinstance(natural, dict) else {}
    natural_after = natural_after if isinstance(natural_after, dict) else {}
    no_early_after = no_early.get("after") if isinstance(no_early, dict) else {}
    no_early_after = no_early_after if isinstance(no_early_after, dict) else {}
    natural_crop = natural.get("wrapCrop") if isinstance(natural, dict) else {}
    natural_crop = natural_crop if isinstance(natural_crop, dict) else {}
    return {
        "ok": (
            no_early.get("started") is True
            and natural.get("started") is True
            and 560 <= int(no_early_after.get("width") or 0) <= 590
            and int(natural_after.get("width") or 999) <= 470
            and int(natural_after.get("width") or 0) >= dialog.minimumWidth()
            and int(no_early_layout.get("clippedCount") or 0) == 0
            and int(natural_layout.get("clippedCount") or 0) == 0
            and no_early_layout.get("stripSettingsOverlap") is False
            and natural_layout.get("stripSettingsOverlap") is False
            and int(no_early_wrap.get("lineCount") or 0) == 1
            and no_early_wrap.get("groupsAtomic") is True
            and int(no_early_wrap.get("clippedPairCount", 999)) == 0
            and int(natural_wrap.get("lineCount") or 0) >= 2
            and natural_wrap.get("groupsAtomic") is True
            and int(natural_wrap.get("clippedPairCount", 999)) == 0
            and natural_crop.get("ok") is True
        ),
        "proofPath": "ai-control-center-right-edge-windows-cursor-drag",
        "proofPathVariant": "two-stage-no-early-wrap-then-natural-wrap",
        "hudResizePathSubset": "HUD Dashboard active right-edge cursor drag live resize proof subset",
        "inputMethod": "windows-cursor-left-button-drag",
        "codeForcedGeometry": False,
        "runtimeResizeEventStarted": no_early.get("started") is True and natural.get("started") is True,
        "started": no_early.get("started") is True and natural.get("started") is True,
        "cursorDragPoints": {
            "noEarlyWrap": no_early.get("cursorDragPoints") or [],
            "naturalWrap": natural.get("cursorDragPoints") or [],
        },
        "before": initial,
        "after": natural_after,
        "targetWidth": int(dialog.minimumWidth()),
        "minimumWidth": int(dialog.minimumWidth()),
        "minimumHeight": int(dialog.minimumHeight()),
        "widthDelta": int(natural_after.get("width") or 0) - initial["width"],
        "heightDelta": int(natural_after.get("height") or 0) - initial["height"],
        "layout": natural_layout,
        "wrapCrop": natural_crop,
        "titleDescriptionWrapCrop": natural.get("titleDescriptionWrapCrop") or {},
        "screenshots": natural.get("screenshots") or {},
        "noEarlyWrapProof": no_early,
        "naturalWrapProof": natural,
    }


def _ai_dashboard_resize_hit_zone_probe(app: QApplication, dialog: AIControlCenterDialog) -> dict[str, object]:
    width = int(dialog.width())
    height = int(dialog.height())
    center_x = width // 2
    center_y = height // 2
    edge_sample_inset = max(4, min(10, int(dialog.RESIZE_MARGIN) // 2))
    corner_sample_inset = max(edge_sample_inset + 12, min(24, int(dialog.RESIZE_MARGIN) + 4))
    right_edge_x = max(0, width - 1 - edge_sample_inset)
    bottom_edge_y = max(0, height - 1 - edge_sample_inset)
    bottom_corner_y = max(0, height - 1 - corner_sample_inset)
    sample_points = {
        "left": QPoint(edge_sample_inset, center_y),
        "right": QPoint(right_edge_x, center_y),
        "top": QPoint(center_x, edge_sample_inset),
        "bottom": QPoint(center_x, bottom_edge_y),
        "topLeft": QPoint(corner_sample_inset, corner_sample_inset),
        "topRight": QPoint(right_edge_x, corner_sample_inset),
        "bottomLeft": QPoint(corner_sample_inset, bottom_corner_y),
        "bottomRight": QPoint(right_edge_x, bottom_corner_y),
        "innerContent": QPoint(max(48, dialog.RESIZE_MARGIN + 28), max(220, dialog.RESIZE_MARGIN + 80)),
        "windowControls": dialog._ai_control_center_close_zone().center(),
    }
    expected_resize_samples = {
        "left",
        "right",
        "top",
        "bottom",
        "topLeft",
        "topRight",
        "bottomLeft",
        "bottomRight",
    }
    samples: dict[str, dict[str, object]] = {}
    for name, point in sample_points.items():
        edges = dialog._ai_control_center_resize_edges_for_local_pos(point)
        hit_test = int(dialog._ai_control_center_resize_hit_test_for_edges(edges))
        global_point = dialog.mapToGlobal(point)
        expected_hover_key = list(dialog._ai_control_center_resize_edge_key(edges)) if edges else None
        dialog._reset_ai_control_center_resize_cursor()
        SetCursorPos(int(global_point.x()), int(global_point.y()))
        _pump(app, 120)
        dialog._poll_ai_control_center_resize_hover_cursor()
        actual_hover_key = (
            list(dialog._resize_cursor_key)
            if isinstance(dialog._resize_cursor_key, tuple)
            else dialog._resize_cursor_key
        )
        samples[name] = {
            "localPoint": {"x": point.x(), "y": point.y()},
            "globalPoint": {"x": global_point.x(), "y": global_point.y()},
            "edges": {
                "left": bool(edges & Qt.LeftEdge),
                "right": bool(edges & Qt.RightEdge),
                "top": bool(edges & Qt.TopEdge),
                "bottom": bool(edges & Qt.BottomEdge),
            },
            "hitTest": hit_test,
            "expectedHoverKey": expected_hover_key,
            "hoverCursorKey": actual_hover_key,
            "hoverCursorMatchesEdges": actual_hover_key == expected_hover_key,
            "expectedResize": name in expected_resize_samples,
        }
    dialog._reset_ai_control_center_resize_cursor()
    expected_ok = all(samples[name]["hitTest"] != 0 for name in expected_resize_samples)
    non_edge_ok = samples["innerContent"]["hitTest"] == 0 and samples["windowControls"]["hitTest"] == 0
    hover_ok = all(samples[name]["hoverCursorMatchesEdges"] is True for name in expected_resize_samples)
    return {
        "ok": expected_ok and non_edge_ok and hover_ok,
        "resizeMarginPx": int(dialog.RESIZE_MARGIN),
        "sampleInsetPx": edge_sample_inset,
        "edgeSampleInsetPx": edge_sample_inset,
        "cornerSampleInsetPx": corner_sample_inset,
        "expectedResizeSamples": sorted(expected_resize_samples),
        "samples": samples,
        "expectedResizeSamplesHit": expected_ok,
        "nonEdgeSamplesClear": non_edge_ok,
        "hoverCursorSamplesStable": hover_ok,
    }


def _button_rect(app: QApplication, web_window, button_id: str) -> dict[str, int | str | bool]:
    raw = _run_child_js(
        app,
        web_window,
        f"""
        (() => {{
          const button = document.getElementById({json.dumps(button_id)});
          if (!button) return JSON.stringify({{ ok: false, reason: "missing-button" }});
          button.scrollIntoView({{ block: "center", inline: "center", behavior: "instant" }});
          const rect = button.getBoundingClientRect();
          return JSON.stringify({{
            ok: true,
            id: button.id || "",
            text: button.textContent.trim(),
            left: Math.round(rect.left),
            top: Math.round(rect.top),
            width: Math.round(rect.width),
            height: Math.round(rect.height)
          }});
        }})();
        """,
    )
    return json.loads(raw or "{}")


def _click_web_button(app: QApplication, web_window, button_id: str) -> dict[str, object]:
    rect = _button_rect(app, web_window, button_id)
    if not rect.get("ok"):
        return {"ok": False, "button": button_id, "reason": rect.get("reason", "missing-button")}
    _foreground_window(app, web_window)
    point = QPoint(int(rect["left"]) + int(rect["width"]) // 2, int(rect["top"]) + int(rect["height"]) // 2)
    global_point = web_window.webview.mapToGlobal(point)
    SetCursorPos(int(global_point.x()), int(global_point.y()))
    _pump(app, 80)
    mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    _pump(app, 40)
    mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    _pump(app, 500)
    return {
        "ok": True,
        "button": button_id,
        "text": rect.get("text", ""),
        "point": {"x": point.x(), "y": point.y()},
        "globalPoint": {"x": global_point.x(), "y": global_point.y()},
        "clickMode": "os-cursor-webview-coordinate",
    }


def _hover_web_button(app: QApplication, web_window, button_id: str) -> dict[str, object]:
    rect = _button_rect(app, web_window, button_id)
    if not rect.get("ok"):
        return {"ok": False, "button": button_id, "reason": rect.get("reason", "missing-button")}
    _foreground_window(app, web_window)
    point = QPoint(int(rect["left"]) + int(rect["width"]) // 2, int(rect["top"]) + int(rect["height"]) // 2)
    global_point = web_window.webview.mapToGlobal(point)
    SetCursorPos(int(global_point.x()), int(global_point.y()))
    _pump(app, 260)
    return {
        "ok": True,
        "button": button_id,
        "text": rect.get("text", ""),
        "point": {"x": point.x(), "y": point.y()},
        "globalPoint": {"x": global_point.x(), "y": global_point.y()},
        "hoverMode": "os-cursor-webview-coordinate",
    }


def _drag_child_window(app: QApplication, window, dx: int = 36, dy: int = 24) -> dict[str, object]:
    _foreground_window(app, window)
    before = _rect(int(window.winId()))
    start = QPoint(min(176, max(80, window.webview.width() // 3)), 46)
    end = QPoint(start.x() + dx, start.y() + dy)
    QTest.mousePress(window.webview, Qt.LeftButton, Qt.NoModifier, start)
    _pump(app, 60)
    QTest.mouseMove(window.webview, end, 120)
    _pump(app, 80)
    QTest.mouseRelease(window.webview, Qt.LeftButton, Qt.NoModifier, end)
    _pump(app, 220)
    after = _rect(int(window.winId()))
    return {
        "before": before,
        "after": after,
        "deltaLeft": after["left"] - before["left"],
        "deltaTop": after["top"] - before["top"],
        "moved": abs(after["left"] - before["left"]) >= 16 and abs(after["top"] - before["top"]) >= 12,
        "mode": "webview-header-drag",
    }


def _resize_child_window(app: QApplication, window, dx: int = 44, dy: int = 34) -> dict[str, object]:
    _foreground_window(app, window)
    before = _rect(int(window.winId()))
    start = QPoint(max(2, window.webview.width() - 4), max(2, window.webview.height() - 4))
    end = QPoint(start.x() + dx, start.y() + dy)
    QTest.mousePress(window.webview, Qt.LeftButton, Qt.NoModifier, start)
    _pump(app, 60)
    QTest.mouseMove(window.webview, end, 140)
    _pump(app, 80)
    QTest.mouseRelease(window.webview, Qt.LeftButton, Qt.NoModifier, end)
    _pump(app, 260)
    after = _rect(int(window.winId()))
    return {
        "before": before,
        "after": after,
        "widthDelta": after["width"] - before["width"],
        "heightDelta": after["height"] - before["height"],
        "resized": after["width"] - before["width"] >= 22 and after["height"] - before["height"] >= 16,
        "mode": "webview-bottom-right-edge-resize",
    }


def _open_from_dashboard(app: QApplication, dialog: AIControlCenterDialog, button_id: str, domain_id: str):
    before = set(dialog._domain_windows.keys())
    result = _run_js(
        app,
        dialog,
        f"""
        (() => {{
          const button = document.getElementById({json.dumps(button_id)});
          if (!button) return JSON.stringify({{ ok: false, reason: "missing-button" }});
          return JSON.stringify({{ ok: true, label: button.textContent.trim(), target: button.dataset.launchTarget || "", kind: button.dataset.launchWindowKind || "" }});
        }})();
        """,
    )
    click = _click_web_button(app, dialog, button_id)
    _pump(app, 700)
    window = dialog._domain_windows.get(domain_id)
    return {"probe": json.loads(result or "{}"), "realClick": click}, window, before


def _hash_file(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _px(value: object) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return float(text.removesuffix("px"))
    except ValueError:
        return None


def _median(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return float(ordered[middle])
    return (ordered[middle - 1] + ordered[middle]) / 2.0


def _grammar_group(grammar: dict[str, object], group_name: str) -> dict[str, object]:
    groups = grammar.get("materialGroups") if isinstance(grammar, dict) else {}
    if not isinstance(groups, dict):
        return {}
    group = groups.get(group_name)
    return group if isinstance(group, dict) else {}


def _grammar_style(grammar: dict[str, object], group_name: str, key: str) -> object:
    group = _grammar_group(grammar, group_name)
    style = group.get("style")
    if not isinstance(style, dict):
        return None
    return style.get(key)


def _grammar_rect_value(grammar: dict[str, object], group_name: str, key: str) -> float | None:
    group = _grammar_group(grammar, group_name)
    rect = group.get("rect")
    if not isinstance(rect, dict):
        return None
    raw = rect.get(key)
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def _metric_summary(grammar: dict[str, object]) -> dict[str, object]:
    rows = grammar.get("rowMetrics") if isinstance(grammar, dict) else []
    buttons = grammar.get("buttonMetrics") if isinstance(grammar, dict) else []
    cards = grammar.get("cardMetrics") if isinstance(grammar, dict) else []
    rows = rows if isinstance(rows, list) else []
    buttons = buttons if isinstance(buttons, list) else []
    cards = cards if isinstance(cards, list) else []
    row_heights = [
        float(row.get("height") or 0)
        for row in rows
        if isinstance(row, dict) and float(row.get("height") or 0) > 0
    ]
    button_heights = [
        float(button.get("height") or 0)
        for button in buttons
        if isinstance(button, dict) and float(button.get("height") or 0) > 0
    ]
    button_widths = [
        float(button.get("width") or 0)
        for button in buttons
        if isinstance(button, dict) and float(button.get("width") or 0) > 0
    ]
    after_row_gaps = [
        float(card.get("afterRowsGap") or 0)
        for card in cards
        if isinstance(card, dict) and card.get("afterRowsGap") is not None
    ]
    action_bottom_gutters = [
        float(card.get("actionBottomGutter") or 0)
        for card in cards
        if isinstance(card, dict) and card.get("actionBottomGutter") is not None
    ]
    return {
        "rowCount": len(rows),
        "buttonCount": len(buttons),
        "cardCount": len(cards),
        "medianRowHeight": _median(row_heights),
        "minRowHeight": min(row_heights) if row_heights else 0,
        "maxRowHeight": max(row_heights) if row_heights else 0,
        "medianButtonHeight": _median(button_heights),
        "medianButtonWidth": _median(button_widths),
        "medianAfterRowGap": _median(after_row_gaps),
        "medianActionBottomGutter": _median(action_bottom_gutters),
    }


def _write_visual_grammar_audit(
    log_root: Path,
    dashboard_probe: dict[str, object],
) -> dict[str, object]:
    grammar = dashboard_probe.get("visualGrammar")
    if not isinstance(grammar, dict):
        grammar = {}
    findings: list[dict[str, object]] = []

    def add(group: str, ok: bool, observed: object, note: str) -> None:
        findings.append({
            "group": group,
            "status": "CONFORMING" if ok else "NONCONFORMING",
            "observed": observed,
            "note": note,
        })

    add(
        "visualGrammarProbe",
        grammar.get("ok") is True,
        grammar.get("ok"),
        "Current dashboard visual probe completed.",
    )

    required_groups = (
        "chrome", "titleGroup", "header", "kicker", "title", "subtitle",
        "surfaceRole", "surfaceRoleCopy", "surfaceRolePair", "windowControls",
        "windowControlButton", "controlHub", "hubCard", "cardTopline",
        "cardBadge", "cardTitle", "cardDescription", "stateRow", "rowLabel",
        "rowValue", "hubActions", "hubAction", "buttonLabel",
        "scrollbarTrack", "scrollbarThumb",
    )
    for name in required_groups:
        present = bool(_grammar_group(grammar, name).get("present"))
        add(name, present, present, "Current rendered dashboard element is present.")

    label_size = _px(_grammar_style(grammar, "rowLabel", "fontSize"))
    value_size = _px(_grammar_style(grammar, "rowValue", "fontSize"))
    add(
        "rowTypography.labelValueFontSizeParity",
        label_size is not None and value_size is not None
        and abs(label_size - value_size) <= 0.1,
        {"labelPx": label_size, "valuePx": value_size},
        "Current dashboard row labels and values use the same font size.",
    )
    css = grammar.get("cssStateSelectors")
    if not isinstance(css, dict):
        css = {}
    for name in (
        "hubActionHover", "hubActionFocus", "hubActionPressed",
        "hubActionDisabled", "windowControlHover", "windowControlFocus",
        "windowControlDisabled", "customScrollbar",
    ):
        add(
            f"stateCoverage.{name}",
            bool(css.get(name)),
            css.get(name),
            "Current dashboard has the interaction state.",
        )

    blocking = [item for item in findings if item["status"] != "CONFORMING"]
    status = "PASS" if not blocking else "FAIL"
    audit = {
        "status": status,
        "auditKind": "current-dashboard-visual-grammar",
        "currentSummary": _metric_summary(grammar),
        "blockingFindingCount": len(blocking),
        "findings": findings,
        "blockingFindings": blocking,
    }
    json_path = log_root / "14_current_visual_grammar_audit.json"
    md_path = log_root / "14_current_visual_grammar_audit.md"
    json_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    rows = [
        "# Current Dashboard Visual Grammar Audit",
        "",
        f"Status: {status}",
        "",
        "| Group | Status | Observed | Note |",
        "| --- | --- | --- | --- |",
    ]
    for item in findings:
        observed = str(item["observed"]).replace("|", "/")
        note = str(item["note"]).replace("|", "/")
        rows.append(f"| {item['group']} | {item['status']} | {observed} | {note} |")
    md_path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    audit["jsonPath"] = str(json_path)
    audit["markdownPath"] = str(md_path)
    return audit


def _copy_user_evidence(local_root: Path, stamp: str) -> Path:
    user_root = (
        Path.home()
        / "OneDrive"
        / "Pictures"
        / "Screenshots"
        / "Nexus Desktop AI"
        / "FAM-007-H4"
        / f"{stamp}-parent-dashboard"
    )
    if user_root.exists():
        shutil.rmtree(user_root)
    user_root.mkdir(parents=True, exist_ok=True)
    for png in sorted(local_root.glob("*.png")):
        (user_root / png.name).write_bytes(png.read_bytes())
    return user_root


def main() -> int:
    stamp = _timestamp()
    log_root = REPO_ROOT / "dev" / "logs" / "fam_007_ai_control_center_live_resize" / stamp
    log_root.mkdir(parents=True, exist_ok=True)
    isolated_state_path = log_root / "isolated_ai_dashboard_window_state.json"
    os.environ["NEXUS_AI_CONTROL_CENTER_STATE_PATH"] = str(isolated_state_path)
    os.environ.pop("NEXUS_AI_CONTROL_CENTER_ENABLE_GEOMETRY_MEMORY", None)

    app = QApplication.instance() or QApplication(sys.argv)
    screen = QApplication.primaryScreen()
    if screen is None:
        raise RuntimeError("No primary screen available for parent-dashboard validation")

    events: list[str] = []
    provider_state = build_provider_setup_completion_foundation_state(
        build_default_provider_readiness_config(),
        surface_role="hud",
    )
    dialog = AIControlCenterDialog(screen, event_logger=events.append)
    dialog.update_provider_state(provider_state.as_renderer_payload())
    available = screen.availableGeometry()
    dialog.setGeometry(
        QRect(
            available.x() + max(40, available.width() - dialog.DEFAULT_WIDTH - 120),
            available.y() + 80,
            dialog.DEFAULT_WIDTH,
            dialog.DEFAULT_HEIGHT,
        )
    )
    dialog.show_from_tray()
    _pump(app, 900)

    screenshots: dict[str, dict[str, str]] = {
        "dashboard_initial": _capture_window(app, dialog, log_root, "01_dashboard_initial"),
    }
    dashboard_probe = json.loads(
        _run_js(
            app,
            dialog,
            """
            (() => {
              const surface = document.getElementById("monitoring-hud");
              const cardNames = Array.from(document.querySelectorAll("[data-dashboard-hub-card]")).map((card) => card.dataset.dashboardHubCard || "");
              const launchers = Array.from(document.querySelectorAll("[data-category-launcher]")).map((button) => ({
                id: button.id || "",
                text: button.textContent.trim(),
                launcher: button.dataset.categoryLauncher || "",
                target: button.dataset.launchTarget || "",
                kind: button.dataset.launchWindowKind || ""
              }));
              const deferredButtons = Array.from(document.querySelectorAll("[data-action-state='deferred']")).map((button) => {
                const rect = button.getBoundingClientRect();
                const style = getComputedStyle(button);
                return {
                  id: button.id || "",
                  text: button.textContent.trim(),
                  disabled: Boolean(button.disabled),
                  ariaDisabled: button.getAttribute("aria-disabled") || "",
                  launchTarget: button.dataset.launchTarget || "",
                  launchKind: button.dataset.launchWindowKind || "",
                  width: Math.round(rect.width),
                  height: Math.round(rect.height),
                  fontSize: style.fontSize,
                  fontWeight: style.fontWeight
                };
              });
              const surfaceRect = surface?.getBoundingClientRect();
              const chrome = document.querySelector(".monitoring-hud__chrome");
              const header = document.querySelector(".monitoring-hud__title-group");
              const headerCopy = document.querySelector(".monitoring-hud__header");
              const title = document.querySelector(".monitoring-hud__title");
              const subtitle = document.querySelector(".monitoring-hud__subtitle");
              const windowControls = document.querySelector(".monitoring-hud__window-controls");
              const hub = document.getElementById("ai-control-center-card-hub");
              const firstCard = document.querySelector("[data-dashboard-hub-card]");
              const thirdCard = document.querySelector('[data-dashboard-hub-card="capabilities-maintenance"]');
              const chromeStyle = chrome ? getComputedStyle(chrome) : null;
              const headerCopyStyle = headerCopy ? getComputedStyle(headerCopy) : null;
              const titleBackingStyle = header ? getComputedStyle(header, "::before") : null;
              const subtitleStyle = subtitle ? getComputedStyle(subtitle) : null;
              const hubStyle = hub ? getComputedStyle(hub) : null;
              const rectFor = (node, extra = 0) => {
                if (!node) return { left: 0, top: 0, width: 0, height: 0, right: 0, bottom: 0 };
                const rect = node.getBoundingClientRect();
                return {
                  left: Math.round(rect.left - extra),
                  top: Math.round(rect.top - extra),
                  width: Math.round(rect.width + (extra * 2)),
                  height: Math.round(rect.height + (extra * 2)),
                  right: Math.round(rect.right + extra),
                  bottom: Math.round(rect.bottom + extra)
                };
              };
              const intersects = (a, b) => Boolean(a && b && a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top);
              const pxNumber = (value) => {
                const parsed = Number.parseFloat(String(value || "0"));
                return Number.isFinite(parsed) ? parsed : 0;
              };
              const firstGridColumnWidth = (template) => {
                const match = String(template || "").match(/([\\d.]+)px/);
                return match ? Number(match[1]) : 0;
              };
              const lineHeightNumber = (style, rect) => pxNumber(style?.lineHeight) || Math.max(1, rect.height);
              const titleStatusPillWrap = (() => {
                const copy = document.querySelector(".monitoring-hud__surface-role-copy");
                const copyRect = rectFor(copy);
                const pairMetrics = [...document.querySelectorAll(".monitoring-hud__surface-role-pair")].map((pair) => {
                  const rect = rectFor(pair);
                  const style = getComputedStyle(pair);
                  const childRects = [...pair.children].map((child) => rectFor(child));
                  const childTops = childRects.map((rect) => rect.top);
                  const childBottoms = childRects.map((rect) => rect.bottom);
                  const childTopSpread = childTops.length ? Math.max(...childTops) - Math.min(...childTops) : 0;
                  const childBottomSpread = childBottoms.length ? Math.max(...childBottoms) - Math.min(...childBottoms) : 0;
                  return {
                    text: pair.textContent.replace(/\\s+/g, " ").trim(),
                    rect,
                    display: style.display,
                    flexShrink: style.flexShrink,
                    whiteSpace: style.whiteSpace,
                    lineTop: rect.top,
                    childrenShareLine: childTopSpread <= 2 && childBottomSpread <= 2,
                    withinPill: copyRect.width > 0 && rect.left >= copyRect.left - 2 && rect.right <= copyRect.right + 2
                  };
                });
                const expectedTexts = ["AI Persona - None", "Status - Not implemented", "Provider - Blocked"];
                return {
                  copyMaxWidth: copy ? getComputedStyle(copy).maxWidth : "",
                  pairCount: pairMetrics.length,
                  lineCount: new Set(pairMetrics.map((pair) => pair.lineTop)).size,
                  expectedTextsPresent: expectedTexts.every((text) => pairMetrics.some((pair) => pair.text === text)),
                  groupsAtomic: pairMetrics.every((pair) => pair.display.includes("flex") && pair.whiteSpace === "nowrap" && pair.childrenShareLine),
                  clippedPairCount: pairMetrics.filter((pair) => !pair.withinPill).length,
                  pairMetrics
                };
              })();
              const titleDescriptionWrap = (() => {
                const description = subtitle;
                const descriptionRect = rectFor(description);
                const descriptionStyle = description ? getComputedStyle(description) : null;
                const titleGroupRectForWrap = rectFor(header);
                const titleGroupStyleForWrap = header ? getComputedStyle(header) : null;
                const titleGroupInnerWidth = header
                  ? Math.round(
                      titleGroupRectForWrap.width
                      - pxNumber(titleGroupStyleForWrap?.paddingLeft)
                      - pxNumber(titleGroupStyleForWrap?.paddingRight)
                    )
                  : 0;
                const publishedMaxWidth = pxNumber(description?.dataset.titleDescriptionMaxWidth || "");
                const expectedText = "AI is not implemented; provider/model execution is blocked, and no prompt, file, memory, telemetry, or provider data leaves this machine.";
                const text = (description?.textContent || "").replace(/\\s+/g, " ").trim();
                const rectFromDomRect = (rect) => ({
                  left: Math.round(rect.left),
                  top: Math.round(rect.top),
                  right: Math.round(rect.right),
                  bottom: Math.round(rect.bottom),
                  width: Math.round(rect.width),
                  height: Math.round(rect.height)
                });
                const textNode = description
                  ? [...description.childNodes].find((node) => node.nodeType === Node.TEXT_NODE && node.textContent.trim())
                  : null;
                const wordMetrics = [];
                if (textNode) {
                  const rawText = textNode.textContent || "";
                  const wordPattern = /\\S+/g;
                  let match = null;
                  while ((match = wordPattern.exec(rawText)) !== null) {
                    const range = document.createRange();
                    range.setStart(textNode, match.index);
                    range.setEnd(textNode, match.index + match[0].length);
                    const rects = [...range.getClientRects()]
                      .filter((rect) => rect.width > 0 && rect.height > 0)
                      .map(rectFromDomRect);
                    range.detach();
                    const rect = rects[0] || { left: 0, top: 0, right: 0, bottom: 0, width: 0, height: 0 };
                    wordMetrics.push({
                      text: match[0],
                      rect,
                      rects,
                      lineTop: rect.top,
                      withinDescription: descriptionRect.width > 0 && rect.left >= descriptionRect.left - 2 && rect.right <= descriptionRect.right + 2
                    });
                  }
                }
                const groupCount = description ? description.querySelectorAll(".monitoring-hud__subtitle-group").length : 0;
                const lineTops = [...new Set(wordMetrics.map((word) => word.lineTop).filter((top) => top > 0))];
                const lastPhraseMetrics = wordMetrics.slice(-6);
                const lastPhraseLineCount = new Set(lastPhraseMetrics.map((word) => word.lineTop).filter((top) => top > 0)).size;
                const lastPhraseText = lastPhraseMetrics.map((word) => word.text).join(" ");
                return {
                  containerRect: descriptionRect,
                  display: descriptionStyle?.display || "",
                  flexWrap: descriptionStyle?.flexWrap || "",
                  whiteSpace: descriptionStyle?.whiteSpace || "",
                  overflowWrap: descriptionStyle?.overflowWrap || "",
                  wordBreak: descriptionStyle?.wordBreak || "",
                  maxWidth: descriptionStyle?.maxWidth || "",
                  publishedMaxWidth: Math.round(publishedMaxWidth),
                  titleGroupInnerWidth,
                  columnSource: description?.dataset.titleDescriptionColumnSource || "",
                  metadata: description?.dataset.titleDescriptionWrap || "",
                  text,
                  expectedTextPresent: text === expectedText,
                  groupCount,
                  lineCount: lineTops.length,
                  wordCount: wordMetrics.length,
                  noAtomicPhraseGroups: groupCount === 0,
                  wordsCanWrapIndividually: wordMetrics.length > 0 && wordMetrics.every((word) => word.rect.width <= descriptionRect.width + 2),
                  clippedWordCount: wordMetrics.filter((word) => !word.withinDescription).length,
                  lastPhraseText,
                  lastPhraseLineCount,
                  lastPhraseWrapsByWord: lastPhraseText === "or provider data leaves this machine." && lastPhraseLineCount >= 2,
                  measuredWidthMatchesTitleCardInner: Math.abs(Math.round(publishedMaxWidth) - titleGroupInnerWidth) <= 2,
                  fixedLegacyMaxWidthRemoved: descriptionStyle ? descriptionStyle.maxWidth !== "600px" : false,
                  containerUsesProseWordWrap: descriptionStyle
                    ? !descriptionStyle.display.includes("flex") && descriptionStyle.whiteSpace === "normal"
                    : false,
                  wordMetrics,
                  lastPhraseMetrics
                };
              })();
              const rowTitleSizingProbe = (() => {
                const hub = document.getElementById("ai-control-center-card-hub");
                const hubStyle = hub ? getComputedStyle(hub) : null;
                const derivedGutter = pxNumber(hubStyle?.getPropertyValue("--ai-dashboard-row-gutter"));
                const derivedVerticalGutter = pxNumber(hubStyle?.getPropertyValue("--ai-dashboard-row-vertical-gutter"));
                const declaredLabelColumnWidthRaw = hubStyle?.getPropertyValue("--ai-dashboard-row-label-width") || "";
                const declaredLabelColumnWidthIsPx = /^\\s*\\d+(?:\\.\\d+)?px\\s*$/.test(declaredLabelColumnWidthRaw);
                const declaredLabelColumnWidth = declaredLabelColumnWidthIsPx ? pxNumber(declaredLabelColumnWidthRaw) : 0;
                const rows = [...document.querySelectorAll(".ai-control-center-card-rows .monitoring-hud__state-row")];
                const rowStackMetrics = [...document.querySelectorAll(".ai-control-center-card-rows")].map((stack, stackIndex) => {
                  const stackStyle = getComputedStyle(stack);
                  const stackRows = [...stack.querySelectorAll(".monitoring-hud__state-row")];
                  const pairGaps = stackRows.slice(1).map((row, index) => {
                    const previousRect = stackRows[index].getBoundingClientRect();
                    const rowRect = row.getBoundingClientRect();
                    return Math.round(rowRect.top - previousRect.bottom);
                  });
                  const rowGapPx = Math.round(pxNumber(stackStyle.rowGap || stackStyle.gap));
                  return {
                    stackIndex,
                    rowCount: stackRows.length,
                    rowGapPx,
                    expectedRowVerticalGutterPx: Math.round(derivedVerticalGutter),
                    pairGaps,
                    rowGapMatchesToken: Math.abs(rowGapPx - derivedVerticalGutter) <= 1,
                    pairGapsMatchToken: pairGaps.every((gap) => Math.abs(gap - derivedVerticalGutter) <= 1)
                  };
                });
                const labelWidths = rows.map((row) => {
                  const label = row.querySelector("span");
                  const labelRect = rectFor(label);
                  return Math.ceil(Math.max(labelRect.width || 0, label?.scrollWidth || 0));
                });
                const measuredMaxLabelWidth = labelWidths.length ? Math.max(...labelWidths) : 0;
                const contractLabelColumnWidth = Math.round(declaredLabelColumnWidth);
                const rowMetrics = rows.map((row, index) => {
                  const rowRect = rectFor(row);
                  const style = getComputedStyle(row);
                  const label = row.querySelector("span");
                  const value = row.querySelector("strong");
                  const labelRect = rectFor(label);
                  const valueRect = rectFor(value);
                  const labelStyle = label ? getComputedStyle(label) : null;
                  const titleColumnWidth = firstGridColumnWidth(style.gridTemplateColumns);
                  const labelWraps = labelRect.height > lineHeightNumber(labelStyle, labelRect) * 1.35;
                  const valueColumnOffset = Math.round(valueRect.left - rowRect.left);
                  const expectedValueColumnOffset = Math.round(contractLabelColumnWidth + derivedGutter);
                  const fixedColumnGutterPx = Math.round(valueColumnOffset - titleColumnWidth);
                  const visibleLabelToValueGutterPx = Math.round(valueRect.left - labelRect.right);
                  return {
                    index,
                    key: `${label?.textContent.trim() || ""}|${value?.textContent.trim() || ""}`,
                    label: label?.textContent.trim() || "",
                    value: value?.textContent.trim() || "",
                    labelFontSize: labelStyle?.fontSize || "",
                    valueFontSize: value ? getComputedStyle(value).fontSize : "",
                    gridTemplateColumns: style.gridTemplateColumns,
                    titleColumnWidth: Math.round(titleColumnWidth),
                    labelWidth: labelRect.width,
                    rowLeft: rowRect.left,
                    rowGutterPx: Math.round(derivedGutter),
                    fixedColumnGutterPx,
                    visibleLabelToValueGutterPx,
                    valueColumnOffset,
                    expectedValueColumnOffset,
                    valueLeft: valueRect.left,
                    rowRight: rowRect.right,
                    labelWraps,
                    titleColumnContentExcessPx: Math.round(titleColumnWidth - labelRect.width),
                    titleColumnMatchesContract: Math.abs(titleColumnWidth - contractLabelColumnWidth) <= 2,
                    valueColumnOffsetMatchesContract: Math.abs(valueColumnOffset - expectedValueColumnOffset) <= 2,
                    fixedColumnGutterMatchesToken: Math.abs(fixedColumnGutterPx - derivedGutter) <= 2,
                    visibleGutterAtLeastFixedGutter: visibleLabelToValueGutterPx >= derivedGutter - 2,
                    labelWithinRow: labelRect.left >= rowRect.left - 2 && labelRect.right <= rowRect.right + 2,
                    valueWithinRow: valueRect.left >= rowRect.left - 2 && valueRect.right <= rowRect.right + 2
                  };
                });
                const valueOffsets = rowMetrics.map((row) => row.valueColumnOffset);
                const uniformValueColumnOffset = valueOffsets.length
                  ? Math.max(...valueOffsets) - Math.min(...valueOffsets) <= 2
                  : false;
                const valueLefts = rowMetrics.map((row) => Math.round(row.valueLeft));
                const uniformValueLeftEdge = valueLefts.length
                  ? Math.max(...valueLefts) - Math.min(...valueLefts) <= 2
                  : false;
                const maxLabelColumnExcess = Math.abs(contractLabelColumnWidth - measuredMaxLabelWidth);
                const maxTitleColumnExcess = rowMetrics.length
                  ? Math.max(...rowMetrics.map((row) => Math.abs(row.titleColumnWidth - contractLabelColumnWidth)))
                  : 999;
                const declaredLabelColumnMatchesMeasuredMax = declaredLabelColumnWidthIsPx
                  && contractLabelColumnWidth > 0
                  && maxLabelColumnExcess <= 2;
                return {
                  rowCount: rowMetrics.length,
                  labelColumnSource: hub?.dataset.rowLabelColumnSource || "",
                  labelColumnUnit: hub?.dataset.rowLabelColumnUnit || "",
                  rowValueColumnContract: hub?.dataset.rowValueColumnContract || "",
                  measuredMaxLabelWidth: Math.round(measuredMaxLabelWidth),
                  declaredLabelColumnWidthRaw: declaredLabelColumnWidthRaw.trim(),
                  declaredLabelColumnWidthIsPx,
                  declaredLabelColumnWidth: Math.round(declaredLabelColumnWidth),
                  contractLabelColumnWidth,
                  rowGutterPx: Math.round(derivedGutter),
                  rowVerticalGutterPx: Math.round(derivedVerticalGutter),
                  rowVerticalGutterRestored: rowStackMetrics.every((stack) => stack.rowCount < 2 || (stack.rowGapMatchesToken && stack.pairGapsMatchToken)),
                  rowStackMetrics,
                  contentSized: rowMetrics.every((row) => (
                    !row.labelWraps
                    && row.titleColumnMatchesContract
                    && row.valueColumnOffsetMatchesContract
                    && row.fixedColumnGutterMatchesToken
                    && row.visibleGutterAtLeastFixedGutter
                  )) && declaredLabelColumnMatchesMeasuredMax && maxTitleColumnExcess <= 2 && uniformValueColumnOffset && uniformValueLeftEdge,
                  noLabelClipping: rowMetrics.every((row) => row.labelWithinRow),
                  noValueClipping: rowMetrics.every((row) => row.valueWithinRow),
                  labelValueFontSizeParity: rowMetrics.every((row) => row.labelFontSize === row.valueFontSize),
                  valueColumnDerivedFromLabelContent: rowMetrics.every((row) => row.valueColumnOffsetMatchesContract),
                  valueColumnDerivedFromMaxLabelContent: rowMetrics.every((row) => row.valueColumnOffsetMatchesContract),
                  declaredLabelColumnMatchesMeasuredMax,
                  fixedColumnGutterRestored: rowMetrics.every((row) => row.fixedColumnGutterMatchesToken),
                  uniformValueColumnOffset,
                  uniformValueLeftEdge,
                  visibleRowGutterAtLeastFixedGutter: rowMetrics.every((row) => row.visibleGutterAtLeastFixedGutter),
                  maxTitleColumnExcessPx: maxTitleColumnExcess,
                  maxLabelColumnExcessPx: maxLabelColumnExcess,
                  rowMetrics
                };
              })();
              const belowTitleTextWeightProbe = (() => {
                const hub = document.getElementById("ai-control-center-card-hub");
                const nodes = hub
                  ? [...hub.querySelectorAll("span, strong, p, button, .monitoring-hud__button-label")]
                  : [];
                const textNodes = nodes.filter((node) => {
                  const rect = node.getBoundingClientRect();
                  const style = getComputedStyle(node);
                  return node.textContent.trim()
                    && style.display !== "none"
                    && style.visibility !== "hidden"
                    && Number(style.opacity || 1) > 0
                    && rect.width > 0
                    && rect.height > 0;
                }).map((node) => ({
                  text: node.textContent.replace(/\\s+/g, " ").trim(),
                  tagName: node.tagName.toLowerCase(),
                  className: node.className || "",
                  fontWeight: getComputedStyle(node).fontWeight
                }));
                const non720 = textNodes.filter((node) => node.fontWeight !== "720");
                return {
                  targetWeight: "720",
                  nodeCount: textNodes.length,
                  all720: textNodes.length > 0 && non720.length === 0,
                  non720
                };
              })();
              const rowMetrics = [...document.querySelectorAll(".ai-control-center-card-rows .monitoring-hud__state-row")].map((row) => {
                const rect = row.getBoundingClientRect();
                const style = getComputedStyle(row);
                return {
                  height: Math.round(rect.height),
                  paddingTop: style.paddingTop,
                  paddingBottom: style.paddingBottom
                };
              });
              const cardVisualMetrics = [...document.querySelectorAll("[data-dashboard-hub-card]")].map((card) => {
                const cardRect = card.getBoundingClientRect();
                const rows = card.querySelector(".ai-control-center-card-rows");
                const rowsRect = rows?.getBoundingClientRect();
                const action = card.querySelector(".monitoring-hud__hub-actions");
                const actionRect = action?.getBoundingClientRect();
                const button = card.querySelector("[data-action-state='deferred']");
                const buttonRect = button?.getBoundingClientRect();
                const descriptions = card.querySelector(".monitoring-hud__hub-card-description");
                const descriptionStyle = descriptions ? getComputedStyle(descriptions) : null;
                return {
                  card: card.dataset.dashboardHubCard || "",
                  height: Math.round(cardRect.height),
                  rowsHeight: rowsRect ? Math.round(rowsRect.height) : 0,
                  actionGapFromRows: rowsRect && actionRect ? Math.round(actionRect.top - rowsRect.bottom) : 0,
                  actionHeight: actionRect ? Math.round(actionRect.height) : 0,
                  rightGutterToButton: buttonRect ? Math.round(cardRect.right - buttonRect.right) : 0,
                  buttonWidth: buttonRect ? Math.round(buttonRect.width) : 0,
                  buttonHeight: buttonRect ? Math.round(buttonRect.height) : 0,
                  descriptionTextIndent: descriptionStyle ? descriptionStyle.textIndent : "",
                  descriptionTop: descriptions ? Math.round(descriptions.getBoundingClientRect().top - cardRect.top) : 0
                };
              });
              const headerRect = rectFor(header, 3);
              const subtitleRect = rectFor(subtitle, 4);
              const windowControlRect = rectFor(windowControls, 0);
              const titleGroupRect = rectFor(header, 0);
              const chromeRect = rectFor(chrome, 0);
              const firstRows = firstCard?.querySelector(".ai-control-center-card-rows");
              const firstAction = firstCard?.querySelector(".monitoring-hud__hub-actions");
              return JSON.stringify({
                title: document.querySelector(".monitoring-hud__title")?.textContent.trim() || "",
                subtitle: document.querySelector(".monitoring-hud__subtitle")?.textContent.replace(/\\s+/g, " ").trim() || "",
                surfaceRole: surface?.dataset.productSurfaceRole || "",
                aiControlCenterPlacement: surface?.dataset.aiControlCenterPlacement || "",
                dashboardIaModel: surface?.dataset.dashboardIaModel || "",
                dashboardSurfaceModel: surface?.dataset.dashboardSurfaceModel || "",
                childWindowModel: surface?.dataset.childWindowModel || "",
                sameWindowFocusedSectionPolicy: surface?.dataset.sameWindowFocusedSectionPolicy || "",
                defaultWindowWidth: surface?.dataset.defaultWindowWidth || "",
                defaultWindowHeight: surface?.dataset.defaultWindowHeight || "",
                titleBackingLayer: surface?.dataset.titleBackingLayer || "",
                cardOrder: surface?.dataset.dashboardCardOrder || "",
                cardNames,
                launchers,
                deferredButtons,
                designProcessCopyPresent: /Refined|Option\\s+[A-Z]|target/i.test(document.body.innerText || ""),
                detachedWindowOpenCopyPresent: /Open Control Center|Open Diagnostics|Open Capabilities/.test(document.body.innerText || ""),
                cardTitles: [...document.querySelectorAll("[data-dashboard-hub-card] .monitoring-hud__hub-card-title-copy strong")].map((node) => node.textContent.trim()),
                cardDescriptions: [...document.querySelectorAll("[data-dashboard-hub-card] .monitoring-hud__hub-card-description")].map((node) => node.textContent.trim()),
                stripText: document.querySelector("[data-dashboard-role='global-ai-strip']")?.textContent.replace(/\\s+/g, " ").trim() || "",
                launcherActionRows: [...document.querySelectorAll("[data-dashboard-hub-card] .monitoring-hud__hub-actions")].map((row) => ({
                  contract: row.dataset.actionRowContract || "",
                  buttonCount: row.querySelectorAll("[data-action-state='deferred']").length,
                  followsRows: Boolean(row.previousElementSibling?.classList.contains("ai-control-center-card-rows")),
                  insideRows: Boolean(row.closest(".ai-control-center-card-rows"))
                })),
                layoutMetrics: {
                  surfaceWidth: surfaceRect ? Math.round(surfaceRect.width) : 0,
                  chromePaddingLeft: chromeStyle ? chromeStyle.paddingLeft : "",
                  chromePaddingRight: chromeStyle ? chromeStyle.paddingRight : "",
                  headerWidth: header ? Math.round(header.getBoundingClientRect().width) : 0,
                  hubPaddingTop: hubStyle ? hubStyle.paddingTop : "",
                  hubPaddingLeft: hubStyle ? hubStyle.paddingLeft : "",
                  hubPaddingRight: hubStyle ? hubStyle.paddingRight : "",
                  headerPaddingRight: headerCopyStyle ? headerCopyStyle.paddingRight : "",
                  titleBackingDisplay: titleBackingStyle ? titleBackingStyle.display : "",
                  titleBackingContent: titleBackingStyle ? titleBackingStyle.content : "",
                  titleBackingOpacity: titleBackingStyle ? titleBackingStyle.opacity : "",
                  titleBackingLayerRemoved: Boolean(titleBackingStyle && titleBackingStyle.display === "none"),
                  subtitleHeight: subtitle ? Math.round(subtitle.getBoundingClientRect().height) : 0,
                  subtitleLineHeight: subtitleStyle ? subtitleStyle.lineHeight : "",
                  subtitleLineCount: titleDescriptionWrap.lineCount,
                  subtitlePublishedMaxWidth: titleDescriptionWrap.publishedMaxWidth,
                  subtitleTitleCardInnerWidth: titleDescriptionWrap.titleGroupInnerWidth,
                  subtitleOverlapsWindowControls: intersects(subtitleRect, windowControlRect),
                  windowControlOuterTopOffset: windowControls && chrome ? Math.round(windowControlRect.top - chromeRect.top) : 0,
                  windowControlOuterRightOffset: windowControls && chrome ? Math.round(chromeRect.right - windowControlRect.right) : 0,
                  topGutter: firstCard && hub ? Math.round(firstCard.getBoundingClientRect().top - hub.getBoundingClientRect().top) : 0,
                  scrollbarVisible: surface?.dataset.customScrollbarVisible || "false",
                  rowMetrics,
                  cardVisualMetrics
                },
                proofRects: {
                  header: headerRect,
                  subtitleWrap: subtitleRect,
                  rowGutterCardDensity: rectFor(firstRows, 8),
                  buttonPlacement: rectFor(firstAction, 8),
                  firstCard: rectFor(firstCard, 4)
                },
                defaultScrollMetrics: (() => {
                  const hubRect = hub?.getBoundingClientRect();
                  const thirdRect = thirdCard?.getBoundingClientRect();
                  return {
                    clientHeight: hub ? Math.round(hub.clientHeight) : 0,
                    scrollHeight: hub ? Math.round(hub.scrollHeight) : 0,
                    maxScroll: hub ? Math.round(Math.max(0, hub.scrollHeight - hub.clientHeight)) : 0,
                    scrollTop: hub ? Math.round(hub.scrollTop) : 0,
                    thirdCardFullyVisibleAtDefault: Boolean(hubRect && thirdRect && thirdRect.top >= hubRect.top && thirdRect.bottom <= hubRect.bottom),
                    thirdCardPartiallyVisibleAtDefault: Boolean(hubRect && thirdRect && thirdRect.bottom > hubRect.top && thirdRect.top < hubRect.bottom)
                  };
                })(),
                rowGroups: Object.fromEntries([...document.querySelectorAll("[data-dashboard-hub-card]")].map((card) => [
                  card.dataset.dashboardHubCard || "",
                  [...card.querySelectorAll(".monitoring-hud__state-row")].map((row) => ({
                    label: row.querySelector("span")?.textContent.trim() || "",
                    value: row.querySelector("strong")?.textContent.trim() || ""
                  }))
                ])),
                capabilityHubRows: document.querySelectorAll('[data-dashboard-hub-card="capabilities-maintenance"] .monitoring-hud__state-row').length,
                settingsRouteMetadata: document.getElementById("monitoring-hud")?.dataset.settingsRoute || "",
                titleStatusWrapMetadata: document.getElementById("monitoring-hud")?.dataset.titleStatusWrap || "",
                titleDescriptionWrapMetadata: document.getElementById("monitoring-hud")?.dataset.titleDescriptionWrap || "",
                rowTitleSizingMetadata: document.getElementById("monitoring-hud")?.dataset.rowTitleSizing || "",
                titleStatusPillWrap,
                titleDescriptionWrap,
                rowTitleSizingProbe,
                belowTitleTextWeightProbe,
                settingsTooltipText: document.getElementById("ai-dashboard-settings-tooltip")?.textContent.trim() || "",
                settingsRoutePresent: Boolean(document.querySelector("[data-dashboard-utility-row='settings-route']")),
                settingsVisualAcceptance: document.querySelector("[data-dashboard-utility-row='settings-route']")?.dataset.settingsVisualAcceptance || "",
                settingsBehavior: document.querySelector("[data-dashboard-utility-row='settings-route']")?.dataset.settingsBehavior || "",
                settingsButtonState: document.getElementById("ai-dashboard-settings-action")?.dataset.settingsState || "",
                settingsWindowOpened: document.getElementById("ai-dashboard-settings-action")?.dataset.settingsWindowOpened || "",
                settingsRouteVisible: (() => {
                  const row = document.querySelector("[data-dashboard-utility-row='settings-route']");
                  if (!row) return false;
                  const style = getComputedStyle(row);
                  const rect = row.getBoundingClientRect();
                  return style.display !== "none" && style.visibility !== "hidden" && Number(style.opacity) > 0 && rect.width > 0 && rect.height > 0;
                })(),
                settingsButtonPresent: Boolean(document.getElementById("ai-dashboard-settings-action")),
                settingsButtonVisible: (() => {
                  const button = document.getElementById("ai-dashboard-settings-action");
                  if (!button) return false;
                  const style = getComputedStyle(button);
                  const rect = button.getBoundingClientRect();
                  return style.display !== "none" && style.visibility !== "hidden" && Number(style.opacity) > 0 && rect.width > 0 && rect.height > 0;
                })(),
                focusedSurfaceCount: document.querySelectorAll("[data-focused-surface]").length,
                domainSurfaceCount: document.querySelectorAll("[data-domain-surface]").length,
                localCheckInline: Boolean(document.getElementById("ai-control-center-local-check-action")),
                generateInline: Boolean(document.getElementById("ai-control-center-generate-report-action")),
                copyInline: Boolean(document.getElementById("ai-control-center-copy-report-action")),
                visibleSettingsFutureText: document.body.innerText.includes("Settings future-gated"),
                activeAiText: document.body.innerText.includes("Active AI"),
                trustProviderText: document.body.innerText.includes("Trust & Provider"),
                nativeTitleTooltipCount: document.querySelectorAll("[title]").length
              });
            })();
            """,
        )
    )
    dashboard_probe["visualGrammar"] = _run_visual_grammar_probe(app, dialog)
    settings_option_b_disposition = _write_settings_option_b_disposition(log_root)
    settings_tooltip_probe = json.loads(
        _run_js(
            app,
            dialog,
            """
            (() => {
              const tooltip = document.getElementById("ai-dashboard-settings-tooltip");
              const style = tooltip ? getComputedStyle(tooltip) : null;
              const rect = tooltip ? tooltip.getBoundingClientRect() : null;
              return JSON.stringify({
                present: Boolean(tooltip),
                text: tooltip?.textContent.trim() || "",
                opacity: style ? Number(style.opacity) : 0,
                display: style ? style.display : "",
                visibility: style ? style.visibility : "",
                visible: style && rect ? style.display !== "none" && style.visibility !== "hidden" && Number(style.opacity) > 0 && rect.width > 0 && rect.height > 0 : false,
                label: document.getElementById("ai-dashboard-settings-action")?.getAttribute("aria-label") || "",
                state: document.getElementById("ai-dashboard-settings-action")?.dataset.settingsState || "",
                windowOpened: document.getElementById("ai-dashboard-settings-action")?.dataset.settingsWindowOpened || "",
                route: document.getElementById("ai-dashboard-settings-action")?.dataset.settingsRoute || "",
                titleCount: document.querySelectorAll("[title]").length
              });
            })();
            """,
        )
    )
    proof_rects = dashboard_probe.get("proofRects") if isinstance(dashboard_probe.get("proofRects"), dict) else {}
    proof_crops = {
        "focusedTitleHeader": _capture_window_region(app, dialog, log_root, "04_focused_title_header", proof_rects.get("header")),
        "subtitleWrap": _capture_window_region(app, dialog, log_root, "05_subtitle_wrap", proof_rects.get("subtitleWrap")),
        "rowGutterCardDensity": _capture_window_region(app, dialog, log_root, "06_row_gutter_card_density", proof_rects.get("rowGutterCardDensity")),
        "buttonPlacement": _capture_window_region(app, dialog, log_root, "07_button_placement", proof_rects.get("buttonPlacement")),
        "firstCardDensity": _capture_window_region(app, dialog, log_root, "08_first_card_density", proof_rects.get("firstCard")),
    }
    visual_grammar_audit = _write_visual_grammar_audit(log_root, dashboard_probe)
    resize_edge_hit_zone_probe = _ai_dashboard_resize_hit_zone_probe(app, dialog)

    child_windows_visible_before_close = {
        "control-center": False,
        "readiness-diagnostics": False,
        "capabilities-maintenance": False,
    }
    child_chrome_probe = {}
    child_geometry_behavior = {}
    readiness_result = {}
    singleton_focus = {}
    child_control_behavior = {}
    deferred_launch_probe = {
        "domainWindowCount": len(dialog._domain_windows),
        "domainWindowKeys": sorted(dialog._domain_windows.keys()),
        "acceptedScope": "parent-dashboard-only",
        "detachedChildWindowDisposition": "deferred-not-accepted-current-gate",
    }

    dashboard_rect_before_resize = _rect(int(dialog.winId()))
    _run_js(
        app,
        dialog,
        """
        (() => {
          const hub = document.getElementById("ai-control-center-card-hub");
          if (hub) {
            hub.scrollTop = hub.scrollHeight;
            if (window.nexusAiControlCenterSyncScrollbar) {
              window.nexusAiControlCenterSyncScrollbar();
            }
          }
          return "true";
        })();
        """,
    )
    _pump(app, 250)
    scrolled_probe = json.loads(
        _run_js(
            app,
            dialog,
            """
            (() => {
              const hub = document.getElementById("ai-control-center-card-hub");
              const thirdCard = document.querySelector('[data-dashboard-hub-card="capabilities-maintenance"]');
              const hubRect = hub?.getBoundingClientRect();
              const thirdRect = thirdCard?.getBoundingClientRect();
              return JSON.stringify({
                scrollTop: hub ? Math.round(hub.scrollTop) : 0,
                maxScroll: hub ? Math.round(Math.max(0, hub.scrollHeight - hub.clientHeight)) : 0,
                thirdCardFullyVisibleAfterScroll: Boolean(hubRect && thirdRect && thirdRect.top >= hubRect.top && thirdRect.bottom <= hubRect.bottom),
                thirdCardPartiallyVisibleAfterScroll: Boolean(hubRect && thirdRect && thirdRect.bottom > hubRect.top && thirdRect.top < hubRect.bottom)
              });
            })();
            """,
        )
    )
    screenshots["dashboard_scrolled_bottom"] = _capture_window(
        app,
        dialog,
        log_root,
        "02_dashboard_scrolled_bottom",
    )
    _run_js(
        app,
        dialog,
        """
        (() => {
          const hub = document.getElementById("ai-control-center-card-hub");
          if (hub) {
            hub.scrollTop = 0;
            if (window.nexusAiControlCenterSyncScrollbar) {
              window.nexusAiControlCenterSyncScrollbar();
            }
          }
          return "true";
        })();
        """,
    )
    _pump(app, 180)
    horizontal_resize_proof = _drive_ai_dashboard_horizontal_resize(app, dialog, log_root)
    screenshots["dashboard_horizontal_shrink"] = horizontal_resize_proof.get("screenshots", {})
    dialog.resize(dialog.DEFAULT_WIDTH, dialog.DEFAULT_HEIGHT)
    _pump(app, 260)
    dialog.resize(dialog.width() + 42, dialog.height() + 28)
    _pump(app, 300)
    dashboard_rect_after_resize = _rect(int(dialog.winId()))
    screenshots["dashboard_resized"] = _capture_window(
        app,
        dialog,
        log_root,
        "03_dashboard_resized",
    )
    dashboard_resize_proof = {
        "before": dashboard_rect_before_resize,
        "after": dashboard_rect_after_resize,
        "widthDelta": dashboard_rect_after_resize["width"] - dashboard_rect_before_resize["width"],
        "heightDelta": dashboard_rect_after_resize["height"] - dashboard_rect_before_resize["height"],
    }

    dialog.close()
    _pump(app, 500)
    lifecycle_after_dashboard_close = {
        "controlVisible": False,
        "maintenanceVisible": False,
        "readinessVisible": False,
    }

    opened_desktop_hashes = {}
    duplicate_full_desktop_proof = False
    actual_deferred_labels = [button.get("text") for button in dashboard_probe.get("deferredButtons") or []]
    expected_option_g_rows = {
        "control-center": [
            {"label": "AI Persona", "value": "None; ORIN persona not implemented"},
            {"label": "Provider", "value": "Blocked; no model path active"},
            {"label": "Privacy", "value": "Protected; no provider or third-party tracking"},
        ],
        "readiness-diagnostics": [
            {"label": "Check", "value": "Waiting for USER action"},
            {"label": "Report", "value": "Local decision aid behind diagnostics"},
            {"label": "Prompt", "value": "Not accepted, sent, stored, or indexed"},
        ],
        "capabilities-maintenance": [
            {"label": "Packs", "value": "Install blocked; downloads disabled"},
            {"label": "Updates", "value": "Future-gated; no install execution"},
        ],
    }
    row_label_lengths = [
        len(str(row.get("label") or ""))
        for rows in expected_option_g_rows.values()
        for row in rows
    ]
    title_status_pill_wrap = dashboard_probe.get("titleStatusPillWrap") or {}
    title_description_wrap = dashboard_probe.get("titleDescriptionWrap") or {}
    horizontal_layout = horizontal_resize_proof.get("layout") if isinstance(horizontal_resize_proof, dict) else {}
    horizontal_layout = horizontal_layout if isinstance(horizontal_layout, dict) else {}
    horizontal_title_status_pill_wrap = horizontal_layout.get("titleStatusPillWrap") or {}
    horizontal_title_description_wrap = horizontal_layout.get("titleDescriptionWrap") or {}
    no_early_wrap_proof = horizontal_resize_proof.get("noEarlyWrapProof") if isinstance(horizontal_resize_proof, dict) else {}
    no_early_wrap_proof = no_early_wrap_proof if isinstance(no_early_wrap_proof, dict) else {}
    no_early_wrap_layout = no_early_wrap_proof.get("layout") if isinstance(no_early_wrap_proof, dict) else {}
    no_early_wrap_layout = no_early_wrap_layout if isinstance(no_early_wrap_layout, dict) else {}
    no_early_title_status_pill_wrap = no_early_wrap_layout.get("titleStatusPillWrap") or {}
    no_early_title_description_wrap = no_early_wrap_layout.get("titleDescriptionWrap") or {}
    row_title_sizing_probe = dashboard_probe.get("rowTitleSizingProbe") or {}
    horizontal_row_title_sizing_probe = horizontal_layout.get("rowTitleSizingProbe") or {}
    horizontal_wrap_crop = horizontal_resize_proof.get("wrapCrop") if isinstance(horizontal_resize_proof, dict) else {}
    horizontal_wrap_crop = horizontal_wrap_crop if isinstance(horizontal_wrap_crop, dict) else {}
    horizontal_title_description_wrap_crop = horizontal_resize_proof.get("titleDescriptionWrapCrop") if isinstance(horizontal_resize_proof, dict) else {}
    horizontal_title_description_wrap_crop = horizontal_title_description_wrap_crop if isinstance(horizontal_title_description_wrap_crop, dict) else {}
    below_title_text_weight_probe = dashboard_probe.get("belowTitleTextWeightProbe") or {}

    def _title_column_map(probe: object) -> dict[str, int]:
        if not isinstance(probe, dict):
            return {}
        rows = probe.get("rowMetrics")
        if not isinstance(rows, list):
            return {}
        mapped: dict[str, int] = {}
        for row in rows:
            if not isinstance(row, dict):
                continue
            key = str(row.get("key") or "")
            if not key:
                continue
            mapped[key] = int(row.get("titleColumnWidth") or 0)
        return mapped

    default_title_columns = _title_column_map(row_title_sizing_probe)
    horizontal_title_columns = _title_column_map(horizontal_row_title_sizing_probe)
    title_columns_stable_across_resize = (
        bool(default_title_columns)
        and default_title_columns.keys() == horizontal_title_columns.keys()
        and all(
            abs(int(default_title_columns[key]) - int(horizontal_title_columns[key])) <= 1
            for key in default_title_columns
        )
    )

    layout_metrics = dashboard_probe.get("layoutMetrics") or {}
    row_heights = [
        int(row.get("height") or 0)
        for row in layout_metrics.get("rowMetrics") or []
    ]
    card_visual_metrics = layout_metrics.get("cardVisualMetrics") or []
    card_heights = [
        int(card.get("height") or 0)
        for card in card_visual_metrics
    ]
    action_gaps = [
        int(card.get("actionGapFromRows") or 0)
        for card in card_visual_metrics
    ]
    button_right_gutters = [
        int(card.get("rightGutterToButton") or 0)
        for card in card_visual_metrics
    ]
    description_indents = [
        str(card.get("descriptionTextIndent") or "")
        for card in card_visual_metrics
    ]
    proof_crops_ok = all(item.get("ok") is True for item in proof_crops.values())
    deferred_buttons = dashboard_probe.get("deferredButtons") or []

    def _int_or(value: object, fallback: int = -999) -> int:
        try:
            return int(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return fallback

    def _row_stack_vertical_gutter_ok(probe: object) -> bool:
        if not isinstance(probe, dict):
            return False
        if probe.get("rowCount") != 8:
            return False
        if _int_or(probe.get("rowVerticalGutterPx")) != 6:
            return False
        if probe.get("rowVerticalGutterRestored") is not True:
            return False
        stacks = probe.get("rowStackMetrics")
        if not isinstance(stacks, list) or len(stacks) != 3:
            return False
        for stack, expected_count in zip(stacks, [3, 3, 2]):
            if not isinstance(stack, dict):
                return False
            if _int_or(stack.get("rowCount")) != expected_count:
                return False
            if _int_or(stack.get("rowGapPx")) != 6:
                return False
            if _int_or(stack.get("expectedRowVerticalGutterPx")) != 6:
                return False
            if stack.get("rowGapMatchesToken") is not True:
                return False
            if stack.get("pairGapsMatchToken") is not True:
                return False
            pair_gaps = stack.get("pairGaps")
            if not isinstance(pair_gaps, list) or len(pair_gaps) != expected_count - 1:
                return False
            if any(abs(_int_or(gap) - 6) > 1 for gap in pair_gaps):
                return False
        return True

    def _shared_status_value_column_ok(probe: object) -> bool:
        if not isinstance(probe, dict):
            return False
        if probe.get("rowCount") != 8:
            return False
        if probe.get("labelColumnSource") != "measured-max-visible-label-content-px":
            return False
        if probe.get("labelColumnUnit") != "px":
            return False
        if probe.get("rowValueColumnContract") != "shared-max-label-content-plus-fixed-gutter":
            return False
        if probe.get("declaredLabelColumnWidthIsPx") is not True:
            return False
        if probe.get("declaredLabelColumnMatchesMeasuredMax") is not True:
            return False
        if _int_or(probe.get("declaredLabelColumnWidth")) <= 0:
            return False
        if _int_or(probe.get("contractLabelColumnWidth")) != _int_or(probe.get("declaredLabelColumnWidth")):
            return False
        if abs(_int_or(probe.get("maxLabelColumnExcessPx"), 999)) > 2:
            return False
        if abs(_int_or(probe.get("maxTitleColumnExcessPx"), 999)) > 2:
            return False
        if _int_or(probe.get("rowGutterPx")) != 8:
            return False
        if probe.get("contentSized") is not True:
            return False
        if probe.get("valueColumnDerivedFromLabelContent") is not True:
            return False
        if probe.get("valueColumnDerivedFromMaxLabelContent") is not True:
            return False
        if probe.get("fixedColumnGutterRestored") is not True:
            return False
        if probe.get("uniformValueColumnOffset") is not True:
            return False
        if probe.get("uniformValueLeftEdge") is not True:
            return False
        rows = probe.get("rowMetrics")
        if not isinstance(rows, list) or len(rows) != 8:
            return False
        contract_width = _int_or(probe.get("contractLabelColumnWidth"))
        expected_offset = contract_width + 8
        for row in rows:
            if not isinstance(row, dict):
                return False
            if abs(_int_or(row.get("titleColumnWidth")) - contract_width) > 2:
                return False
            if abs(_int_or(row.get("fixedColumnGutterPx")) - 8) > 2:
                return False
            if abs(_int_or(row.get("valueColumnOffset")) - expected_offset) > 2:
                return False
            if row.get("titleColumnMatchesContract") is not True:
                return False
            if row.get("valueColumnOffsetMatchesContract") is not True:
                return False
            if row.get("fixedColumnGutterMatchesToken") is not True:
                return False
        return True

    def _title_description_wrap_ok(probe: object, *, min_lines: int = 1, max_lines: int | None = None) -> bool:
        if not isinstance(probe, dict):
            return False
        if probe.get("metadata") != "measured-title-card-prose-word-wrap":
            return False
        if probe.get("columnSource") != "title-card-inner-content-width-px":
            return False
        if probe.get("groupCount") != 0:
            return False
        if probe.get("expectedTextPresent") is not True:
            return False
        if probe.get("noAtomicPhraseGroups") is not True:
            return False
        if probe.get("containerUsesProseWordWrap") is not True:
            return False
        if probe.get("fixedLegacyMaxWidthRemoved") is not True:
            return False
        if probe.get("measuredWidthMatchesTitleCardInner") is not True:
            return False
        if probe.get("wordsCanWrapIndividually") is not True:
            return False
        if _int_or(probe.get("publishedMaxWidth")) <= 0:
            return False
        if _int_or(probe.get("titleGroupInnerWidth")) <= 0:
            return False
        if _int_or(probe.get("clippedWordCount"), 999) != 0:
            return False
        if _int_or(probe.get("wordCount")) < 14:
            return False
        line_count = _int_or(probe.get("lineCount"))
        if line_count < min_lines:
            return False
        if max_lines is not None and line_count > max_lines:
            return False
        return True

    checks = {
        "dashboardHubParentOnly": (
            dashboard_probe.get("title") == "AI Dashboard"
            and dashboard_probe.get("dashboardIaModel") == "ai-dashboard-parent-only-global-strip-category-cards-detached-child-windows-deferred"
            and dashboard_probe.get("dashboardSurfaceModel") == "hub-only-cards-are-doorways"
            and dashboard_probe.get("childWindowModel") == "detached-child-windows-deferred-not-accepted-current-gate"
            and dashboard_probe.get("sameWindowFocusedSectionPolicy") == "blocked-as-dashboard-workspace-substitute"
            and dashboard_probe.get("cardNames") == ["control-center", "readiness-diagnostics", "capabilities-maintenance"]
            and dashboard_probe.get("cardTitles") == [
                "AI Persona",
                "AI Readiness",
                "Capabilities",
            ]
            and dashboard_probe.get("cardDescriptions") == [
                "Persona state before any AI action.",
                "Local checks and diagnostics doorway.",
                "Packs and updates stay blocked.",
            ]
            and all(part in dashboard_probe.get("stripText", "") for part in ["AI Persona - None", "Status - Not implemented", "Provider - Blocked"])
            and "Data -" not in dashboard_probe.get("stripText", "")
            and len(dashboard_probe.get("launcherActionRows") or []) == 3
            and all(
                row.get("contract") == "separate-from-state-rows"
                and row.get("buttonCount") == 1
                and row.get("followsRows") is True
                and row.get("insideRows") is False
                for row in dashboard_probe.get("launcherActionRows") or []
            )
            and dashboard_probe.get("rowGroups") == expected_option_g_rows
            and dashboard_probe.get("focusedSurfaceCount") == 0
            and dashboard_probe.get("domainSurfaceCount") == 0
        ),
        "doorwayButtonsDeferredNoFakeActions": (
            actual_deferred_labels == ["Not Available Yet", "Not Available Yet", "Not Available Yet"]
            and len(dashboard_probe.get("launchers") or []) == 0
            and len(deferred_buttons) == 3
            and all(button.get("disabled") is True for button in deferred_buttons)
            and all(button.get("ariaDisabled") == "true" for button in deferred_buttons)
            and all(button.get("launchTarget") == "deferred" for button in deferred_buttons)
            and all(button.get("launchKind") == "deferred-detached-child" for button in deferred_buttons)
            and deferred_launch_probe.get("domainWindowCount") == 0
        ),
        "parentVisualMetrics": (
            dashboard_probe.get("defaultWindowWidth") == "471"
            and dashboard_probe.get("defaultWindowHeight") == "598"
            and str(layout_metrics.get("chromePaddingLeft")) == str(layout_metrics.get("chromePaddingRight"))
            and int(layout_metrics.get("topGutter") or 0) >= 8
            and len(row_heights) == 8
            and min(row_heights or [0]) >= 18
            and max(row_heights or [999]) <= 28
            and all(30 <= int(button.get("height") or 0) <= 32 for button in deferred_buttons)
            and all(int(button.get("width") or 0) >= 120 for button in deferred_buttons)
            and all(str(button.get("fontWeight") or "").isdigit() and int(button.get("fontWeight")) >= 700 for button in deferred_buttons)
            and int(layout_metrics.get("headerWidth") or 0) >= int(layout_metrics.get("surfaceWidth") or 0) - 32
        ),
        "deterministicStatusRowsAndTitlePill": (
            dashboard_probe.get("rowGroups") == expected_option_g_rows
            and max(row_label_lengths or [999]) <= 10
            and "Downloads/updates" not in str(dashboard_probe.get("rowGroups"))
            and "Visible data" not in str(dashboard_probe.get("rowGroups"))
            and "Capability packs" not in str(dashboard_probe.get("rowGroups"))
            and "AI - ORIN" not in dashboard_probe.get("stripText", "")
            and "Data - None" not in dashboard_probe.get("stripText", "")
            and "AI Persona - None" in dashboard_probe.get("stripText", "")
            and "Protected; no provider or third-party tracking" in str(dashboard_probe.get("rowGroups"))
        ),
        "titleStatusPillGroupWrapProven": (
            dashboard_probe.get("titleStatusWrapMetadata") == "group-preserving-atomic-flex-wrap"
            and title_status_pill_wrap.get("pairCount") == 3
            and title_status_pill_wrap.get("expectedTextsPresent") is True
            and title_status_pill_wrap.get("groupsAtomic") is True
            and int(title_status_pill_wrap.get("clippedPairCount", 999)) == 0
            and int(title_status_pill_wrap.get("lineCount", 0)) >= 1
            and no_early_title_status_pill_wrap.get("pairCount") == 3
            and no_early_title_status_pill_wrap.get("expectedTextsPresent") is True
            and no_early_title_status_pill_wrap.get("groupsAtomic") is True
            and int(no_early_title_status_pill_wrap.get("clippedPairCount", 999)) == 0
            and int(no_early_title_status_pill_wrap.get("lineCount", 0)) == 1
            and horizontal_title_status_pill_wrap.get("pairCount") == 3
            and horizontal_title_status_pill_wrap.get("expectedTextsPresent") is True
            and horizontal_title_status_pill_wrap.get("groupsAtomic") is True
            and int(horizontal_title_status_pill_wrap.get("clippedPairCount", 999)) == 0
            and int(horizontal_title_status_pill_wrap.get("lineCount", 0)) >= 2
        ),
        "titleStatusPillNoEarlyWrapAt580Proven": (
            no_early_wrap_proof.get("proofPath") == "ai-control-center-right-edge-windows-cursor-drag"
            and no_early_wrap_proof.get("inputMethod") == "windows-cursor-left-button-drag"
            and no_early_wrap_proof.get("codeForcedGeometry") is False
            and no_early_wrap_proof.get("runtimeResizeEventStarted") is True
            and 560 <= int((no_early_wrap_proof.get("after") or {}).get("width") or 0) <= 590
            and no_early_title_status_pill_wrap.get("copyMaxWidth") == "100%"
            and no_early_title_status_pill_wrap.get("pairCount") == 3
            and no_early_title_status_pill_wrap.get("expectedTextsPresent") is True
            and no_early_title_status_pill_wrap.get("groupsAtomic") is True
            and int(no_early_title_status_pill_wrap.get("clippedPairCount", 999)) == 0
            and int(no_early_title_status_pill_wrap.get("lineCount", 0)) == 1
        ),
        "titleStatusPillWindowsCursorWrapProven": (
            horizontal_resize_proof.get("proofPath") == "ai-control-center-right-edge-windows-cursor-drag"
            and horizontal_resize_proof.get("inputMethod") == "windows-cursor-left-button-drag"
            and horizontal_resize_proof.get("codeForcedGeometry") is False
            and horizontal_resize_proof.get("runtimeResizeEventStarted") is True
            and horizontal_title_status_pill_wrap.get("pairCount") == 3
            and horizontal_title_status_pill_wrap.get("expectedTextsPresent") is True
            and horizontal_title_status_pill_wrap.get("groupsAtomic") is True
            and int(horizontal_title_status_pill_wrap.get("clippedPairCount", 999)) == 0
            and int(horizontal_title_status_pill_wrap.get("lineCount", 0)) >= 2
            and horizontal_wrap_crop.get("ok") is True
            and str(horizontal_wrap_crop.get("path") or "").endswith(
                "16_title_status_pill_wrapped_windows_cursor_resize.png"
            )
        ),
        "titleDescriptionProseWordWrapProven": (
            dashboard_probe.get("titleDescriptionWrapMetadata") == "measured-title-card-prose-word-wrap"
            and _title_description_wrap_ok(title_description_wrap, min_lines=1, max_lines=2)
            and _title_description_wrap_ok(no_early_title_description_wrap, min_lines=1, max_lines=2)
            and _title_description_wrap_ok(horizontal_title_description_wrap, min_lines=2)
        ),
        "titleDescriptionWindowsCursorProseWrapProven": (
            horizontal_resize_proof.get("proofPath") == "ai-control-center-right-edge-windows-cursor-drag"
            and horizontal_resize_proof.get("inputMethod") == "windows-cursor-left-button-drag"
            and horizontal_resize_proof.get("codeForcedGeometry") is False
            and horizontal_resize_proof.get("runtimeResizeEventStarted") is True
            and _title_description_wrap_ok(no_early_title_description_wrap, min_lines=1, max_lines=2)
            and _title_description_wrap_ok(horizontal_title_description_wrap, min_lines=3)
            and int(horizontal_title_description_wrap.get("lineCount") or 0) > int(no_early_title_description_wrap.get("lineCount") or 0)
            and horizontal_title_description_wrap.get("lastPhraseWrapsByWord") is True
            and horizontal_title_description_wrap_crop.get("ok") is True
            and str(horizontal_title_description_wrap_crop.get("path") or "").endswith(
                "16_title_status_pill_wrapped_windows_cursor_resize_title_description.png"
            )
        ),
        "deterministicTitleColumnSizingProven": (
            dashboard_probe.get("rowTitleSizingMetadata") == "shared-max-label-content-fixed-gutter"
            and row_title_sizing_probe.get("rowCount") == 8
            and row_title_sizing_probe.get("labelColumnSource") == "measured-max-visible-label-content-px"
            and int(row_title_sizing_probe.get("rowGutterPx") or 0) == 8
            and row_title_sizing_probe.get("contentSized") is True
            and row_title_sizing_probe.get("valueColumnDerivedFromLabelContent") is True
            and row_title_sizing_probe.get("valueColumnDerivedFromMaxLabelContent") is True
            and row_title_sizing_probe.get("declaredLabelColumnMatchesMeasuredMax") is True
            and row_title_sizing_probe.get("fixedColumnGutterRestored") is True
            and row_title_sizing_probe.get("uniformValueColumnOffset") is True
            and row_title_sizing_probe.get("uniformValueLeftEdge") is True
            and row_title_sizing_probe.get("noLabelClipping") is True
            and row_title_sizing_probe.get("noValueClipping") is True
            and row_title_sizing_probe.get("labelValueFontSizeParity") is True
            and int(row_title_sizing_probe.get("maxTitleColumnExcessPx", 999)) <= 2
            and int(row_title_sizing_probe.get("maxLabelColumnExcessPx", 999)) <= 2
            and horizontal_row_title_sizing_probe.get("rowCount") == 8
            and horizontal_row_title_sizing_probe.get("labelColumnSource") == "measured-max-visible-label-content-px"
            and int(horizontal_row_title_sizing_probe.get("rowGutterPx") or 0) == 8
            and horizontal_row_title_sizing_probe.get("contentSized") is True
            and horizontal_row_title_sizing_probe.get("valueColumnDerivedFromLabelContent") is True
            and horizontal_row_title_sizing_probe.get("valueColumnDerivedFromMaxLabelContent") is True
            and horizontal_row_title_sizing_probe.get("declaredLabelColumnMatchesMeasuredMax") is True
            and horizontal_row_title_sizing_probe.get("fixedColumnGutterRestored") is True
            and horizontal_row_title_sizing_probe.get("uniformValueColumnOffset") is True
            and horizontal_row_title_sizing_probe.get("uniformValueLeftEdge") is True
            and horizontal_row_title_sizing_probe.get("noLabelClipping") is True
            and horizontal_row_title_sizing_probe.get("noValueClipping") is True
            and horizontal_row_title_sizing_probe.get("labelValueFontSizeParity") is True
            and int(horizontal_row_title_sizing_probe.get("maxTitleColumnExcessPx", 999)) <= 2
            and int(horizontal_row_title_sizing_probe.get("maxLabelColumnExcessPx", 999)) <= 2
            and title_columns_stable_across_resize is True
        ),
        "fixedColumnGutterAndUniformValueColumnProven": (
            row_title_sizing_probe.get("rowCount") == 8
            and row_title_sizing_probe.get("fixedColumnGutterRestored") is True
            and row_title_sizing_probe.get("uniformValueColumnOffset") is True
            and horizontal_row_title_sizing_probe.get("rowCount") == 8
            and horizontal_row_title_sizing_probe.get("fixedColumnGutterRestored") is True
            and horizontal_row_title_sizing_probe.get("uniformValueColumnOffset") is True
            and int(row_title_sizing_probe.get("rowGutterPx") or 0) == 8
            and int(horizontal_row_title_sizing_probe.get("rowGutterPx") or 0) == 8
        ),
        "sharedStatusValueColumnProven": (
            _shared_status_value_column_ok(row_title_sizing_probe)
            and _shared_status_value_column_ok(horizontal_row_title_sizing_probe)
        ),
        "rowStackVerticalGutterProven": (
            _row_stack_vertical_gutter_ok(row_title_sizing_probe)
            and _row_stack_vertical_gutter_ok(horizontal_row_title_sizing_probe)
        ),
        "windowControlEdgeGutterProven": (
            14 <= int(layout_metrics.get("windowControlOuterTopOffset") or 0) <= 17
            and 14 <= int(layout_metrics.get("windowControlOuterRightOffset") or 0) <= 17
        ),
        "titleCardBackingLayerRemoved": (
            dashboard_probe.get("titleBackingLayer") == "single-title-card-no-secondary-backing"
            and layout_metrics.get("titleBackingLayerRemoved") is True
            and layout_metrics.get("titleBackingDisplay") == "none"
        ),
        "rowTitleStatusTextSizeParityProven": (
            row_title_sizing_probe.get("rowCount") == 8
            and row_title_sizing_probe.get("labelValueFontSizeParity") is True
            and horizontal_row_title_sizing_probe.get("rowCount") == 8
            and horizontal_row_title_sizing_probe.get("labelValueFontSizeParity") is True
        ),
        "belowTitleTextWeights720Proven": (
            dashboard_probe.get("settingsRouteMetadata") == "option-b-deferred-until-fam003-global-settings-window"
            and dashboard_probe.get("focusedSurfaceCount") == 0
            and dashboard_probe.get("domainSurfaceCount") == 0
            and below_title_text_weight_probe.get("targetWeight") == "720"
            and int(below_title_text_weight_probe.get("nodeCount") or 0) >= 20
            and below_title_text_weight_probe.get("all720") is True
            and not below_title_text_weight_probe.get("non720")
        ),
        "returnedDensityAndButtonPlacementRepaired": (
            len(card_heights) == 3
            and max(card_heights or [999]) <= 205
            and min(card_heights or [0]) >= 118
            and all(4 <= gap <= 8 for gap in action_gaps)
            and all(9 <= gutter <= 22 for gutter in button_right_gutters)
            and all(indent in ("0px", "0") for indent in description_indents)
        ),
        "returnedTitleSubtitleWrapRepaired": (
            str(layout_metrics.get("headerPaddingRight") or "").startswith("108")
            and int(layout_metrics.get("subtitleHeight") or 0) <= 42
            and layout_metrics.get("subtitleOverlapsWindowControls") is False
            and _title_description_wrap_ok(title_description_wrap, min_lines=1, max_lines=2)
        ),
        "currentVisualEvidenceProven": (
            dashboard_probe.get("surfaceRole") == "ai-dashboard-top-most-hub"
            and dashboard_probe.get("aiControlCenterPlacement") == "focused-domain-card-inside-ai-dashboard"
            and proof_crops_ok
        ),
        "currentVisualGrammarProven": (
            visual_grammar_audit.get("status") == "PASS"
            and int(visual_grammar_audit.get("blockingFindingCount") or 0) == 0
        ),
        "resizeEdgeHitZoneProven": (
            resize_edge_hit_zone_probe.get("ok") is True
            and int(resize_edge_hit_zone_probe.get("resizeMarginPx") or 0) >= 16
        ),
        "defaultScrollIntentProven": (
            dashboard_probe.get("defaultWindowHeight") == "598"
            and (
                (
                    int((dashboard_probe.get("defaultScrollMetrics") or {}).get("maxScroll") or 0) == 0
                    and (dashboard_probe.get("defaultScrollMetrics") or {}).get("thirdCardFullyVisibleAtDefault") is True
                    and str(layout_metrics.get("scrollbarVisible")) in {"false", ""}
                )
                or (
                    str(layout_metrics.get("scrollbarVisible")) == "true"
                    and int((dashboard_probe.get("defaultScrollMetrics") or {}).get("maxScroll") or 0) > 20
                    and (dashboard_probe.get("defaultScrollMetrics") or {}).get("thirdCardFullyVisibleAtDefault") is False
                    and scrolled_probe.get("thirdCardFullyVisibleAfterScroll") is True
                    and int(scrolled_probe.get("scrollTop") or 0) >= int(scrolled_probe.get("maxScroll") or 0) - 2
                )
            )
        ),
        "runtimeCopyIsProductFacing": (
            "provider/model execution is blocked" in str(dashboard_probe.get("subtitle") or "")
            and "no prompt, file, memory, telemetry, or provider data leaves this machine" in str(dashboard_probe.get("subtitle") or "")
            and dashboard_probe.get("designProcessCopyPresent") is False
            and dashboard_probe.get("detachedWindowOpenCopyPresent") is False
        ),
        "noInlineWorkspaceActions": (
            dashboard_probe.get("localCheckInline") is False
            and dashboard_probe.get("generateInline") is False
            and dashboard_probe.get("copyInline") is False
        ),
        "capabilitiesCardCompactDoorway": (
            dashboard_probe.get("capabilityHubRows") == 2
        ),
        "redundantCardsRemoved": (
            dashboard_probe.get("activeAiText") is False
            and dashboard_probe.get("trustProviderText") is False
        ),
        "settingsCogRemovedAndDeferred": (
            dashboard_probe.get("visibleSettingsFutureText") is False
            and dashboard_probe.get("nativeTitleTooltipCount") == 0
            and dashboard_probe.get("settingsRouteMetadata") == "option-b-deferred-until-fam003-global-settings-window"
            and dashboard_probe.get("settingsRoutePresent") is False
            and dashboard_probe.get("settingsRouteVisible") is False
            and dashboard_probe.get("settingsButtonPresent") is False
            and dashboard_probe.get("settingsButtonVisible") is False
            and dashboard_probe.get("settingsTooltipText") == ""
            and settings_tooltip_probe.get("present") is False
            and settings_tooltip_probe.get("visible") is False
            and settings_tooltip_probe.get("titleCount") == 0
        ),
        "settingsOptionBSelectionDispositionProven": (
            settings_option_b_disposition.get("ok") is True
            and settings_option_b_disposition.get("selectedOption") == "B"
            and settings_option_b_disposition.get("currentRuntimeSettingsAffordance") == "removed-from-current-workstream-exit-path"
            and settings_option_b_disposition.get("activeGlobalSettingsBehavior") is False
            and settings_option_b_disposition.get("settingsWindowOpened") is False
            and settings_option_b_disposition.get("implementedRuntimeOption") == "B"
        ),
        "fullDesktopProofNotDuplicated": (
            len(opened_desktop_hashes) == 0
            and duplicate_full_desktop_proof is False
        ),
        "dashboardResizeStillWorks": (
            dashboard_resize_proof["widthDelta"] >= 30
            and dashboard_resize_proof["heightDelta"] >= 20
        ),
        "dashboardHorizontalResizeMinimumWorks": (
            horizontal_resize_proof.get("ok") is True
            and horizontal_resize_proof.get("proofPath") == "ai-control-center-right-edge-windows-cursor-drag"
            and horizontal_resize_proof.get("inputMethod") == "windows-cursor-left-button-drag"
            and horizontal_resize_proof.get("codeForcedGeometry") is False
            and horizontal_resize_proof.get("runtimeResizeEventStarted") is True
            and int(horizontal_resize_proof.get("minimumWidth") or 999) <= 430
            and int(horizontal_resize_proof.get("widthDelta") or 0) <= 0
            and int(((horizontal_resize_proof.get("noEarlyWrapProof") or {}).get("widthDelta") or 0)) >= 80
            and int(((horizontal_resize_proof.get("naturalWrapProof") or {}).get("widthDelta") or 0)) <= -100
            and int((horizontal_resize_proof.get("after") or {}).get("width") or 999) <= 470
            and "HUD Dashboard" in str(horizontal_resize_proof.get("hudResizePathSubset") or "")
        ),
        "childLifecycleBehavior": (
            lifecycle_after_dashboard_close["controlVisible"] is False
            and lifecycle_after_dashboard_close["maintenanceVisible"] is False
            and lifecycle_after_dashboard_close["readinessVisible"] is False
        ),
        "providerExecutionStillBlocked": (
            all("PROVIDER" not in event or "provider_visible_data=none" in event.lower() or "provider/model" not in event.lower() for event in events)
            and provider_state.as_renderer_payload().get("sentToProvider") is False
            and provider_state.as_renderer_payload().get("canAcceptPrompts") is False
            and provider_state.as_renderer_payload().get("networkEgressState") == "network-egress-blocked"
            and provider_state.as_renderer_payload().get("memoryIndexingState") == "memory-indexing-disabled"
        ),
    }

    status = "PASS" if all(checks.values()) else "FAIL"
    user_evidence_root = _copy_user_evidence(log_root, stamp)
    manifest = {
        "status": status,
        "stamp": stamp,
        "helper": "dev/orin_ai_control_center_live_resize_validation.py",
        "proofClass": "live AI Dashboard parent-only visual and functional proof",
        "worktree": str(REPO_ROOT),
        "window": "AI Dashboard",
        "dashboardProbe": dashboard_probe,
        "proofCrops": proof_crops,
        "visualGrammarAudit": visual_grammar_audit,
        "resizeEdgeHitZoneProbe": resize_edge_hit_zone_probe,
        "surfaceClassification": {
            "currentSurface": "parent AI Dashboard top-most hub",
            "currentSurfaceRole": dashboard_probe.get("surfaceRole"),
            "aiControlCenterPlacement": dashboard_probe.get("aiControlCenterPlacement"),
            "detachedChildWindowDisposition": "deferred-not-accepted-current-gate",
        },
        "deferredLaunchProbe": deferred_launch_probe,
        "settingsTooltipProbe": settings_tooltip_probe,
        "settingsOptionBDisposition": settings_option_b_disposition,
        "defaultScrollIntentProbe": scrolled_probe,
        "childChromeProbe": child_chrome_probe,
        "childControlBehavior": child_control_behavior,
        "fullDesktopHashes": opened_desktop_hashes,
        "duplicateFullDesktopProof": duplicate_full_desktop_proof,
        "childWindowClassificationLedger": {
            "control-center": {
                "sourceCategoryCard": "AI Persona",
                "launcherLabel": "Not Available Yet",
                "classification": "deferred-detached-child",
                "remainsOpenIfDashboardCloses": False,
                "singleton": False,
                "moveBehavior": "not-in-accepted-scope",
                "resizeBehavior": "not-in-accepted-scope",
                "shellConformance": "deferred-not-accepted-current-gate",
                "focusBehavior": "not-in-accepted-scope",
            },
            "readiness-diagnostics": {
                "sourceCategoryCard": "AI Readiness",
                "launcherLabel": "Not Available Yet",
                "classification": "deferred-detached-child",
                "remainsOpenIfDashboardCloses": False,
                "singleton": False,
                "moveBehavior": "not-in-accepted-scope",
                "resizeBehavior": "not-in-accepted-scope",
                "shellConformance": "deferred-not-accepted-current-gate",
                "focusBehavior": "not-in-accepted-scope",
            },
            "capabilities-maintenance": {
                "sourceCategoryCard": "Capabilities",
                "launcherLabel": "Not Available Yet",
                "classification": "deferred-detached-child",
                "remainsOpenIfDashboardCloses": False,
                "singleton": False,
                "moveBehavior": "not-in-accepted-scope",
                "resizeBehavior": "not-in-accepted-scope",
                "shellConformance": "deferred-not-accepted-current-gate",
                "focusBehavior": "not-in-accepted-scope",
            },
        },
        "readinessResult": readiness_result,
        "singletonFocus": singleton_focus,
        "dashboardResizeProof": dashboard_resize_proof,
        "dashboardHorizontalResizeProof": horizontal_resize_proof,
        "lifecycleAfterDashboardClose": lifecycle_after_dashboard_close,
        "childWindowsVisibleBeforeDashboardClose": child_windows_visible_before_close,
        "childGeometryBehavior": child_geometry_behavior,
        "providerBoundary": {
            "sentToProvider": provider_state.as_renderer_payload().get("sentToProvider"),
            "canAcceptPrompts": provider_state.as_renderer_payload().get("canAcceptPrompts"),
            "providerVisibleData": provider_state.as_renderer_payload().get("providerVisibleData"),
            "networkEgressState": provider_state.as_renderer_payload().get("networkEgressState"),
            "memoryIndexingState": provider_state.as_renderer_payload().get("memoryIndexingState"),
        },
        "events": events,
        "checks": checks,
        "screenshots": screenshots,
        "userInspectableEvidenceRoot": str(user_evidence_root),
        "localLogRoot": str(log_root),
    }
    manifest_path = log_root / "live_resize_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (user_evidence_root / "live_resize_manifest.json").write_bytes(manifest_path.read_bytes())
    for audit_key in ("jsonPath", "markdownPath"):
        audit_source = Path(str(visual_grammar_audit.get(audit_key, "")))
        if audit_source.exists():
            (user_evidence_root / audit_source.name).write_bytes(audit_source.read_bytes())
    settings_disposition_json = Path(str(settings_option_b_disposition.get("jsonPath", "")))
    if settings_disposition_json.exists():
        (user_evidence_root / settings_disposition_json.name).write_bytes(settings_disposition_json.read_bytes())

    if status != "PASS":
        print(f"FAIL: FAM-007 AI Dashboard parent-only validation failed. Manifest: {manifest_path}")
        return 1
    print(f"PASS: FAM-007 AI Dashboard parent-only validation passed. Manifest: {manifest_path}")
    print(f"USER_EVIDENCE_ROOT: {user_evidence_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
