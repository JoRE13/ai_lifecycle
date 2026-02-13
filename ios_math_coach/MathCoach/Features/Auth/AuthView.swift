import SwiftUI

struct AuthView: View {
    @State private var mode: AuthMode = .login

    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                Picker("Auth mode", selection: $mode) {
                    Text("Login").tag(AuthMode.login)
                    Text("Register").tag(AuthMode.register)
                }
                .pickerStyle(.segmented)

                if mode == .login {
                    LoginView()
                } else {
                    RegisterView()
                }

                Spacer()
            }
            .padding(20)
            .navigationTitle("AI Math Coach")
            .background(Color(.systemGroupedBackground))
        }
    }
}

private enum AuthMode {
    case login
    case register
}
