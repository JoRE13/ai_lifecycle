import PencilKit
import SwiftUI

struct PencilCanvasView: View {
    @Binding var drawing: PKDrawing

    var body: some View {
        PencilCanvasRepresentable(drawing: $drawing)
            .frame(minHeight: 360)
            .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: 12, style: .continuous)
                    .stroke(Color.gray.opacity(0.25), lineWidth: 1)
            )
    }
}
