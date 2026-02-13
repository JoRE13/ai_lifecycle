import Foundation

@MainActor
final class AuthManager: ObservableObject {
    enum Status {
        case loading
        case unauthenticated
        case authenticated(MeResponse)
    }

    @Published private(set) var status: Status = .loading
    @Published var errorMessage: String?
    @Published var isSubmitting: Bool = false

    private let api: APIClient
    private let keychain: KeychainStore
    private let accessTokenKey = "mathcoach.access_token"
    private var accessToken: String?

    init(api: APIClient = APIClient(), keychain: KeychainStore = KeychainStore()) {
        self.api = api
        self.keychain = keychain
    }

    func bootstrap() async {
        status = .loading
        errorMessage = nil

        if let storedToken = keychain.get(accessTokenKey) {
            accessToken = storedToken
            if await loadProfile(using: storedToken) {
                return
            }
        }

        if await refreshSession() {
            return
        }

        clearSession()
    }

    func login(email: String, password: String) async {
        await submitAuthAction {
            let response = try await api.login(email: email, password: password)
            try await establishSession(with: response.access_token)
        }
    }

    func register(email: String, password: String) async {
        await submitAuthAction {
            let response = try await api.register(email: email, password: password)
            try await establishSession(with: response.access_token)
        }
    }

    func logout() async {
        isSubmitting = true
        defer { isSubmitting = false }

        do {
            try await api.logout()
        } catch {
            // Keep local logout behavior deterministic even if backend logout fails.
        }
        clearSession()
    }

    func query(
        mode: QueryMode,
        problemImage: Data,
        solutionImage: Data
    ) async throws -> QueryResponse {
        let token = try await ensureAccessToken()
        do {
            return try await api.query(
                mode: mode,
                problemImage: problemImage,
                solutionImage: solutionImage,
                accessToken: token
            )
        } catch AppError.unauthorized {
            let refreshedToken = try await refreshAccessToken()
            return try await api.query(
                mode: mode,
                problemImage: problemImage,
                solutionImage: solutionImage,
                accessToken: refreshedToken
            )
        }
    }

    private func submitAuthAction(_ action: () async throws -> Void) async {
        isSubmitting = true
        errorMessage = nil
        defer { isSubmitting = false }

        do {
            try await action()
        } catch let error as LocalizedError {
            errorMessage = error.errorDescription ?? "Authentication failed."
            clearSession()
        } catch {
            errorMessage = error.localizedDescription
            clearSession()
        }
    }

    private func establishSession(with token: String) async throws {
        accessToken = token
        keychain.set(token, for: accessTokenKey)
        guard await loadProfile(using: token) else {
            throw AppError.unauthorized
        }
    }

    private func loadProfile(using token: String) async -> Bool {
        do {
            let me = try await api.me(accessToken: token)
            status = .authenticated(me)
            errorMessage = nil
            return true
        } catch AppError.unauthorized {
            return false
        } catch let error as LocalizedError {
            errorMessage = error.errorDescription
            return false
        } catch {
            errorMessage = error.localizedDescription
            return false
        }
    }

    private func refreshSession() async -> Bool {
        do {
            let token = try await refreshAccessToken()
            return await loadProfile(using: token)
        } catch {
            return false
        }
    }

    private func refreshAccessToken() async throws -> String {
        let response = try await api.refresh()
        accessToken = response.access_token
        keychain.set(response.access_token, for: accessTokenKey)
        return response.access_token
    }

    private func ensureAccessToken() async throws -> String {
        if let token = accessToken {
            return token
        }
        if let token = keychain.get(accessTokenKey) {
            accessToken = token
            return token
        }
        return try await refreshAccessToken()
    }

    private func clearSession() {
        accessToken = nil
        keychain.delete(accessTokenKey)
        status = .unauthenticated
    }
}
