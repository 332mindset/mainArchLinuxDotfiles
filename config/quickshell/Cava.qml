import QtQuick
import Quickshell
import Quickshell.Io

// Runs cava only while `active` and exposes bar heights as 0..1.
// `bars` must match the value in cava.conf.
Scope {
    id: root

    property bool active: false
    readonly property int bars: 32
    property var values: Array(bars).fill(0)

    Process {
        running: root.active
        command: ["cava", "-p", Quickshell.shellPath("cava.conf")]
        stdout: SplitParser {
            onRead: data => {
                const parts = data.split(";");
                const out = [];
                for (let i = 0; i < root.bars; i++)
                    out.push((parseInt(parts[i]) || 0) / 100);
                root.values = out;
            }
        }
        onRunningChanged: if (!running) root.values = Array(root.bars).fill(0)
    }
}
