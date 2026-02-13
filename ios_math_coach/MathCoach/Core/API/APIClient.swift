import Foundation

final class APIClient {
    private let baseURL: URL
    private let session: URLSession
    private let decoder = JSONDecoder()
    private let encoder = JSONEncoder()

    init(baseURL: URL = AppConfig.baseURL, session: URLSession? = nil) {
        self.baseURL = baseURL
        self.session = session ?? APIClient.makeSession()
    }

    func register(email: String, password: String) async throws -> TokenResponse {
        let payload = RegisterRequest(email: email, password: password)
        var request = try makeRequest(endpoint: .register)
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try encode(payload)
        return try await perform(request, decodeAs: TokenResponse.self)
    }

    func login(email: String, password: String) async throws -> TokenResponse {
        let payload = LoginRequest(email: email, password: password)
        var request = try makeRequest(endpoint: .login)
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try encode(payload)
        return try await perform(request, decodeAs: TokenResponse.self)
    }

    func refresh() async throws -> TokenResponse {
        let request = try makeRequest(endpoint: .refresh)
        return try await perform(request, decodeAs: TokenResponse.self)
    }

    func me(accessToken: String) async throws -> MeResponse {
        var request = try makeRequest(endpoint: .me)
        request.setValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization")
        return try await perform(request, decodeAs: MeResponse.self)
    }

    func logout() async throws {
        let request = try makeRequest(endpoint: .logout)
        _ = try await perform(request, decodeAs: LogoutResponse.self)
    }

    func query(
        mode: QueryMode,
        problemImage: Data,
        solutionImage: Data,
        accessToken: String
    ) async throws -> QueryResponse {
        let builder = MultipartBuilder()
        let parts = [
            MultipartPart(
                name: "mode",
                filename: nil,
                contentType: nil,
                data: Data(mode.rawValue.utf8)
            ),
            MultipartPart(
                name: "prob_image",
                filename: "problem.png",
                contentType: "image/png",
                data: problemImage
            ),
            MultipartPart(
                name: "sol_image",
                filename: "solution.png",
                contentType: "image/png",
                data: solutionImage
            )
        ]
        let body = builder.build(parts: parts)

        var request = try makeRequest(endpoint: .query)
        request.setValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization")
        request.setValue("multipart/form-data; boundary=\(builder.boundary)", forHTTPHeaderField: "Content-Type")
        request.httpBody = body
        return try await perform(request, decodeAs: QueryResponse.self)
    }

    private func makeRequest(endpoint: Endpoint) throws -> URLRequest {
        guard let url = endpointURL(for: endpoint) else {
            throw AppError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = endpoint.method
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        request.timeoutInterval = 30
        request.httpShouldHandleCookies = true
        return request
    }

    private func endpointURL(for endpoint: Endpoint) -> URL? {
        guard var components = URLComponents(url: baseURL, resolvingAgainstBaseURL: false) else {
            return nil
        }

        let basePath = components.path.trimmingCharacters(in: CharacterSet(charactersIn: "/"))
        let endpointPath = endpoint.path.trimmingCharacters(in: CharacterSet(charactersIn: "/"))
        components.path = "/" + [basePath, endpointPath].filter { !$0.isEmpty }.joined(separator: "/")
        return components.url
    }

    private func encode<T: Encodable>(_ value: T) throws -> Data {
        do {
            return try encoder.encode(value)
        } catch {
            throw AppError.encodingFailed
        }
    }

    private func perform<Response: Decodable>(
        _ request: URLRequest,
        decodeAs _: Response.Type
    ) async throws -> Response {
        let (data, response): (Data, URLResponse)
        do {
            (data, response) = try await session.data(for: request)
        } catch {
            throw AppError.message(error.localizedDescription)
        }

        guard let httpResponse = response as? HTTPURLResponse else {
            throw AppError.invalidResponse
        }

        guard (200..<300).contains(httpResponse.statusCode) else {
            if httpResponse.statusCode == 401 {
                throw AppError.unauthorized
            }
            let message = parseServerMessage(from: data)
            throw AppError.server(statusCode: httpResponse.statusCode, message: message)
        }

        do {
            return try decoder.decode(Response.self, from: data)
        } catch {
            throw AppError.decodingFailed
        }
    }

    private func parseServerMessage(from data: Data) -> String {
        guard !data.isEmpty else {
            return "No error detail provided."
        }

        if let object = try? JSONSerialization.jsonObject(with: data),
           let dictionary = object as? [String: Any],
           let detail = dictionary["detail"] {
            if let detailString = detail as? String {
                return detailString
            }
            if let detailArray = detail as? [[String: Any]] {
                return detailArray
                    .compactMap { $0["msg"] as? String }
                    .joined(separator: ", ")
            }
            return String(describing: detail)
        }

        return String(decoding: data, as: UTF8.self)
    }

    private static func makeSession() -> URLSession {
        let config = URLSessionConfiguration.default
        config.httpShouldSetCookies = true
        config.httpCookieAcceptPolicy = .always
        config.httpCookieStorage = HTTPCookieStorage.shared
        config.waitsForConnectivity = true
        return URLSession(configuration: config)
    }
}

private struct LogoutResponse: Decodable {
    let ok: Bool
}
