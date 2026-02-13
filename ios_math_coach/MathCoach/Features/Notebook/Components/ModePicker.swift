import SwiftUI

struct ModePicker: View {
    @Binding var mode: QueryMode

    var body: some View {
        Picker("Mode", selection: $mode) {
            ForEach(QueryMode.allCases) { mode in
                Text(mode.displayName).tag(mode)
            }
        }
        .pickerStyle(.segmented)
    }
}
