import QtQuick

// Round icon button; `primary` is the big filled play/pause one.
Rectangle {
    id: root

    property string glyph
    property bool primary: false
    signal clicked

    width: primary ? 54 : 40
    height: width
    radius: width / 2
    opacity: enabled ? 1 : 0.35
    color: primary ? Theme.accent
         : area.containsMouse ? Theme.alpha(Theme.fg, 0.12) : "transparent"
    scale: area.pressed ? 0.9 : 1
    Behavior on scale { NumberAnimation { duration: 120; easing.type: Easing.OutCubic } }
    Behavior on color { ColorAnimation { duration: 150 } }

    Text {
        anchors.centerIn: parent
        text: root.glyph
        color: root.primary ? (Theme.accent.hslLightness > 0.6 ? "#000000" : "#ffffff") : Theme.fg
        font.family: Theme.iconFont
        font.pixelSize: root.primary ? 26 : 22
    }

    MouseArea {
        id: area
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: root.clicked()
    }
}
