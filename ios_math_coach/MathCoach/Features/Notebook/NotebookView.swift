import SwiftUI
import UIKit

struct NotebookView: View {
    @EnvironmentObject private var authManager: AuthManager
    @StateObject private var viewModel = NotebookViewModel()

    @State private var showImagePicker = false
    @State private var showSourceDialog = false
    @State private var imageSourceType: UIImagePickerController.SourceType = .photoLibrary

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    problemImageSection
                    canvasSection
                    controlsSection
                    responseSection
                }
                .padding(16)
            }
            .navigationTitle("Math Notebook")
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Text(userLabel)
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Logout") {
                        Task { await authManager.logout() }
                    }
                }
            }
            .background(Color(.systemGroupedBackground))
            .confirmationDialog("Choose image source", isPresented: $showSourceDialog) {
                Button("Photo Library") {
                    imageSourceType = .photoLibrary
                    showImagePicker = true
                }

                if UIImagePickerController.isSourceTypeAvailable(.camera) {
                    Button("Camera") {
                        imageSourceType = .camera
                        showImagePicker = true
                    }
                }

                Button("Cancel", role: .cancel) {}
            }
            .sheet(isPresented: $showImagePicker) {
                ImagePicker(sourceType: imageSourceType) { image in
                    viewModel.setProblemImage(image)
                }
            }
        }
    }

    private var userLabel: String {
        guard case let .authenticated(me) = authManager.status else {
            return ""
        }
        return me.email
    }

    private var problemImageSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Problem Image")
                .font(.headline)

            if let image = viewModel.problemImage {
                Image(uiImage: image)
                    .resizable()
                    .scaledToFit()
                    .frame(maxHeight: 220)
                    .frame(maxWidth: .infinity)
                    .background(Color(.secondarySystemBackground))
                    .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
            } else {
                Text("Add the original problem image before submitting a query.")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .frame(maxWidth: .infinity, alignment: .leading)
            }

            Button(viewModel.problemImage == nil ? "Add Problem Image" : "Replace Problem Image") {
                showSourceDialog = true
            }
            .buttonStyle(.bordered)
        }
        .padding(14)
        .background(Color(.systemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
    }

    private var canvasSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Your Work")
                .font(.headline)

            PencilCanvasView(drawing: $viewModel.drawing)
        }
        .padding(14)
        .background(Color(.systemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
    }

    private var controlsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            ModePicker(mode: $viewModel.selectedMode)

            PrimaryButton(title: "Submit to Tutor", isLoading: viewModel.isSubmitting) {
                Task {
                    await viewModel.submitQuery(authManager: authManager)
                }
            }

            Button("Clear Canvas", role: .destructive) {
                viewModel.clearCanvas()
            }
            .buttonStyle(.bordered)

            if let error = viewModel.errorMessage {
                Text(error)
                    .font(.footnote)
                    .foregroundStyle(.red)
            }
        }
        .padding(14)
        .background(Color(.systemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
    }

    private var responseSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Tutor Response")
                .font(.headline)

            if let response = viewModel.response {
                QueryResponseCard(response: response)
            } else {
                Text("No response yet. Submit a query after uploading a problem image and writing a step.")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .padding(12)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color(.secondarySystemBackground))
                    .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
            }
        }
        .padding(14)
        .background(Color(.systemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
    }
}
