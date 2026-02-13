import Foundation

@MainActor
final class AuthViewModel: ObservableObject {
    @Published var email: String = ""
    @Published var password: String = ""
    @Published var confirmPassword: String = ""

    func resetFields() {
        password = ""
        confirmPassword = ""
    }

    func validateLogin() -> String? {
        if email.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            return "Email is required."
        }
        if password.count < 8 {
            return "Password must be at least 8 characters."
        }
        return nil
    }

    func validateRegistration() -> String? {
        if let loginError = validateLogin() {
            return loginError
        }
        if password != confirmPassword {
            return "Passwords do not match."
        }
        return nil
    }
}
