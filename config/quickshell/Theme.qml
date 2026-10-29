pragma Singleton

import QtQuick
import Quickshell
import Quickshell.Io

// Colours follow the Waybar palette, so the widgets restyle together with the bar.
Singleton {
    id: root

    property color fg: "#e2e2e2"
    property color fgDim: "#c6c6c6"
    property color muted: "#919191"
    property color surface: "#353535"
    property color accent: "#ffffff"
    readonly property color background: Qt.rgba(0, 0, 0, 0.85)

    readonly property string font: "Adwaita Sans"
    readonly property string iconFont: "Iosevka Nerd Font"

    function alpha(c, a) {
        return Qt.rgba(c.r, c.g, c.b, a);
    }

    function parse(css) {
        const colors = {};
        const re = /@define-color\s+(\w+)\s+(#[0-9a-fA-F]{6,8})\s*;/g;
        let m;
        while ((m = re.exec(css)) !== null)
            colors[m[1]] = m[2];
        if (colors.text) fg = colors.text;
        if (colors.subtext1) fgDim = colors.subtext1;
        if (colors.overlay1) muted = colors.overlay1;
        if (colors.surface1) surface = colors.surface1;
        if (colors.mauve) accent = colors.mauve;
    }

    FileView {
        path: Quickshell.env("HOME") + "/.config/waybar/matugen.css"
        watchChanges: true
        onFileChanged: reload()
        onLoaded: root.parse(text())
    }
}
