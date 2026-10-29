import QtQuick
import QtQuick.Effects

// Image clipped to rounded corners.
Item {
    id: root

    property alias source: img.source
    property real radius: 10
    property real blur: 0
    readonly property bool ready: img.status === Image.Ready

    Image {
        id: img
        anchors.fill: parent
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
        cache: false
        sourceSize: Qt.size(512, 512)
        visible: false
    }

    Item {
        id: mask
        anchors.fill: parent
        layer.enabled: true
        visible: false
        Rectangle {
            anchors.fill: parent
            radius: root.radius
        }
    }

    MultiEffect {
        anchors.fill: parent
        source: img
        visible: root.ready
        maskEnabled: true
        maskSource: mask
        maskThresholdMin: 0.5
        maskSpreadAtMin: 1.0
        blurEnabled: root.blur > 0
        blur: root.blur
        blurMax: 64
    }
}
