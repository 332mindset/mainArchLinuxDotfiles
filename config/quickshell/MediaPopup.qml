import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Wayland
import Quickshell.Hyprland
import Quickshell.Io
import Quickshell.Services.Mpris

// Media card under the right end of Waybar.
// Toggle: `qs ipc call media toggle`; closes on Esc or a click outside.
PanelWindow {
    id: win

    property bool open: false

    readonly property var players: Mpris.players.values
    // -1 = follow whichever player is playing; set by the dots at the bottom.
    property int pinnedIndex: -1
    readonly property MprisPlayer player: {
        if (pinnedIndex >= 0 && pinnedIndex < players.length)
            return players[pinnedIndex];
        return players.find(p => p.isPlaying) ?? players[0] ?? null;
    }

    function fmt(seconds) {
        const s = Math.max(0, Math.floor(seconds || 0));
        return Math.floor(s / 60) + ":" + String(s % 60).padStart(2, "0");
    }

    function icon(code) {
        return String.fromCodePoint(code);
    }

    anchors {
        top: true
        right: true
    }
    // Waybar already reserves its own height, so the gap is counted from its bottom edge.
    margins {
        top: 8
        right: 150
    }
    implicitWidth: 400
    implicitHeight: card.implicitHeight
    exclusiveZone: 0
    color: "transparent"
    visible: open || card.opacity > 0

    WlrLayershell.layer: WlrLayer.Overlay
    WlrLayershell.namespace: "quickshell-media"
    WlrLayershell.keyboardFocus: open ? WlrKeyboardFocus.OnDemand : WlrKeyboardFocus.None

    IpcHandler {
        target: "media"
        function toggle(): void {
            win.open = !win.open;
        }
        function open(): void {
            win.open = true;
        }
        function close(): void {
            win.open = false;
        }
    }

    HyprlandFocusGrab {
        windows: [win]
        active: win.open
        onCleared: win.open = false
    }

    // MPRIS does not push position updates, so poll while it matters.
    Timer {
        running: win.open && !!win.player && win.player.isPlaying
        interval: 500
        repeat: true
        triggeredOnStart: true
        onTriggered: win.player.positionChanged()
    }

    Cava {
        id: cava
        active: win.visible && !!win.player && win.player.isPlaying
    }

    Rectangle {
        id: card

        width: parent.width
        implicitHeight: content.implicitHeight + 36
        radius: 14
        color: Theme.background
        border.width: 1
        border.color: Theme.alpha(Theme.fg, 0.12)
        focus: win.open
        Keys.onEscapePressed: win.open = false

        opacity: win.open ? 1 : 0
        Behavior on opacity {
            NumberAnimation { duration: 220; easing.type: Easing.OutCubic }
        }
        transform: Translate {
            y: win.open ? 0 : -14
            Behavior on y {
                NumberAnimation { duration: 260; easing.type: Easing.OutCubic }
            }
        }

        // Blurred cover as a backdrop.
        RoundedImage {
            anchors.fill: parent
            radius: card.radius
            source: win.player?.trackArtUrl ?? ""
            blur: 1.0
            opacity: 0.35
        }

        ColumnLayout {
            id: content

            anchors {
                left: parent.left
                right: parent.right
                top: parent.top
                margins: 18
            }
            spacing: 14

            // Nothing playing
            Text {
                visible: !win.player
                Layout.fillWidth: true
                Layout.topMargin: 10
                Layout.bottomMargin: 10
                horizontalAlignment: Text.AlignHCenter
                text: win.icon(0xF0386) + "  Ничего не играет"
                color: Theme.muted
                font.family: Theme.font
                font.pixelSize: 15
            }

            RowLayout {
                visible: !!win.player
                spacing: 16

                Rectangle {
                    Layout.preferredWidth: 104
                    Layout.preferredHeight: 104
                    radius: 10
                    color: Theme.alpha(Theme.surface, 0.6)

                    Text {
                        anchors.centerIn: parent
                        visible: !cover.ready
                        text: win.icon(0xF0386)
                        color: Theme.muted
                        font.family: Theme.iconFont
                        font.pixelSize: 40
                    }

                    RoundedImage {
                        id: cover
                        anchors.fill: parent
                        radius: 10
                        source: win.player?.trackArtUrl ?? ""
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 104
                    spacing: 3

                    Text {
                        Layout.fillWidth: true
                        text: (win.player?.identity ?? "").toUpperCase()
                        color: Theme.muted
                        font.family: Theme.font
                        font.pixelSize: 10
                        font.letterSpacing: 1.5
                        elide: Text.ElideRight
                    }
                    Text {
                        Layout.fillWidth: true
                        text: win.player?.trackTitle || "Без названия"
                        color: Theme.fg
                        font.family: Theme.font
                        font.pixelSize: 17
                        font.weight: Font.DemiBold
                        elide: Text.ElideRight
                    }
                    Text {
                        Layout.fillWidth: true
                        visible: text !== ""
                        text: win.player?.trackArtist ?? ""
                        color: Theme.fgDim
                        font.family: Theme.font
                        font.pixelSize: 13
                        elide: Text.ElideRight
                    }

                    Item { Layout.fillHeight: true }

                    // cava visualiser
                    Item {
                        id: viz
                        Layout.fillWidth: true
                        Layout.preferredHeight: 30

                        Row {
                            anchors.fill: parent
                            spacing: 2

                            Repeater {
                                model: cava.bars
                                Rectangle {
                                    required property int index
                                    anchors.bottom: parent.bottom
                                    width: (viz.width - (cava.bars - 1) * 2) / cava.bars
                                    height: Math.max(2, (cava.values[index] ?? 0) * viz.height)
                                    radius: 1.5
                                    color: Theme.alpha(Theme.accent, 0.75)
                                }
                            }
                        }
                    }
                }
            }

            // Progress
            ColumnLayout {
                visible: !!win.player && win.player.lengthSupported && win.player.length > 0
                Layout.fillWidth: true
                spacing: 4

                Item {
                    id: bar
                    Layout.fillWidth: true
                    Layout.preferredHeight: 14

                    readonly property real progress: win.player && win.player.length > 0
                        ? Math.min(1, win.player.position / win.player.length) : 0

                    Rectangle {
                        anchors.verticalCenter: parent.verticalCenter
                        width: parent.width
                        height: seek.containsMouse ? 6 : 4
                        radius: height / 2
                        color: Theme.alpha(Theme.fg, 0.15)
                        Behavior on height { NumberAnimation { duration: 120 } }

                        Rectangle {
                            width: parent.width * bar.progress
                            height: parent.height
                            radius: parent.radius
                            color: Theme.accent
                        }
                    }

                    MouseArea {
                        id: seek
                        anchors.fill: parent
                        hoverEnabled: true
                        enabled: !!win.player && win.player.canSeek
                        cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
                        onClicked: mouse => win.player.position = mouse.x / width * win.player.length
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    Text {
                        text: win.fmt(win.player?.position)
                        color: Theme.muted
                        font.family: Theme.font
                        font.pixelSize: 11
                    }
                    Item { Layout.fillWidth: true }
                    Text {
                        text: win.fmt(win.player?.length)
                        color: Theme.muted
                        font.family: Theme.font
                        font.pixelSize: 11
                    }
                }
            }

            // Controls
            RowLayout {
                visible: !!win.player
                Layout.alignment: Qt.AlignHCenter
                spacing: 22

                MediaButton {
                    glyph: win.icon(0xF04AE)
                    enabled: !!win.player && win.player.canGoPrevious
                    onClicked: win.player.previous()
                }
                MediaButton {
                    glyph: win.icon(win.player?.isPlaying ? 0xF03E4 : 0xF040A)
                    primary: true
                    enabled: !!win.player && win.player.canTogglePlaying
                    onClicked: win.player.togglePlaying()
                }
                MediaButton {
                    glyph: win.icon(0xF04AD)
                    enabled: !!win.player && win.player.canGoNext
                    onClicked: win.player.next()
                }
            }

            // Player switcher, only when there is more than one source
            Row {
                visible: win.players.length > 1
                Layout.alignment: Qt.AlignHCenter
                spacing: 6

                Repeater {
                    model: win.players.length
                    Rectangle {
                        required property int index
                        readonly property bool current: win.players[index] === win.player
                        width: current ? 18 : 6
                        height: 6
                        radius: 3
                        color: current ? Theme.accent : Theme.alpha(Theme.fg, 0.3)
                        Behavior on width { NumberAnimation { duration: 180; easing.type: Easing.OutCubic } }

                        MouseArea {
                            anchors.fill: parent
                            anchors.margins: -4
                            cursorShape: Qt.PointingHandCursor
                            onClicked: win.pinnedIndex = index
                        }
                    }
                }
            }
        }
    }
}
