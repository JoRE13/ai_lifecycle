import PencilKit
import SwiftUI
import UIKit

@MainActor
final class NotebookViewModel: ObservableObject {
    @Published var problemImage: UIImage?
    @Published var drawing: PKDrawing = .init()
    @Published var selectedMode: QueryMode = .hint
    @Published var response: QueryResponse?
    @Published var errorMessage: String?
    @Published var isSubmitting: Bool = false

    func setProblemImage(_ image: UIImage) {
        problemImage = image
    }

    func clearCanvas() {
        drawing = PKDrawing()
    }

    func resetResponse() {
        response = nil
        errorMessage = nil
    }

    func submitQuery(authManager: AuthManager) async {
        isSubmitting = true
        errorMessage = nil
        defer { isSubmitting = false }

        do {
            guard let problemImage else {
                throw AppError.missingProblemImage
            }

            guard let problemData = problemImage.jpegData(compressionQuality: 0.9) ?? problemImage.pngData() else {
                throw AppError.encodingFailed
            }

            let solutionData: Data
            if drawing.bounds.isEmpty {
                if selectedMode == .reveal {
                    let emptyImage = renderEmptyCanvasImage()
                    guard let data = emptyImage.pngData() else {
                        throw AppError.encodingFailed
                    }
                    solutionData = data
                } else {
                    throw AppError.emptyDrawing
                }
            } else {
                let drawingBounds = drawing.bounds.insetBy(dx: -16, dy: -16)
                let image = drawing.image(from: drawingBounds, scale: 2.0)
                guard let data = image.pngData() else {
                    throw AppError.encodingFailed
                }
                solutionData = data
            }

            response = try await authManager.query(
                mode: selectedMode,
                problemImage: problemData,
                solutionImage: solutionData
            )
        } catch let error as LocalizedError {
            errorMessage = error.errorDescription ?? "Query request failed."
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    private func renderEmptyCanvasImage() -> UIImage {
        let size = CGSize(width: 1200, height: 1600)
        let renderer = UIGraphicsImageRenderer(size: size)
        return renderer.image { context in
            UIColor.white.setFill()
            context.fill(CGRect(origin: .zero, size: size))
        }
    }
}
