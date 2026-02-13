import SwiftUI

struct LoginView: View {
    @EnvironmentObject private var authManager: AuthManager
    @StateObject private var viewModel = AuthViewModel()
    @State private var localError: String?

    var body: some View {
        VStack(spacing: 12) {
            TextField("Email", text: $viewModel.email)
                .textInputAutocapitalization(.never)
                .keyboardType(.emailAddress)
                .autocorrectionDisabled()
                .padding(12)
                .background(Color(.secondarySystemBackground))
                .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))

            SecureField("Password", text: $viewModel.password)
                .padding(12)
                .background(Color(.secondarySystemBackground))
                .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))

            if let error = localError ?? authManager.errorMessage {
                Text(error)
                    .font(.footnote)
                    .foregroundStyle(.red)
                    .frame(maxWidth: .infinity, alignment: .leading)
            }

            PrimaryButton(title: "Login", isLoading: authManager.isSubmitting) {
                localError = viewModel.validateLogin()
                guard localError == nil else { return }

                Task {
                    await authManager.login(email: viewModel.email, password: viewModel.password)
                }
            }
        }
        .padding(16)
        .background(Color(.systemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
    }
}
