import type { RegisterPost, LogIn, LogInFail } from "./types";
const BASE_URL = process.env.BASE_URL;

export class ProjectApi {
  async postToApi<T>(
    url: string,
    body: T,
    token?: string,
  ): Promise<Response | null> {
    let response: Response | undefined;
    console.log(JSON.stringify(body));
    try {
      if (token) {
        response = await fetch(url, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify(body),
        });
      } else {
        response = await fetch(url, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(body),
        });
      }
    } catch (e) {
      console.error("error fetching from api", url, e);
      return null;
    }

    return response;
  }

  async register(body: RegisterPost): Promise<LogIn | LogInFail | null> {
    const url = BASE_URL + "/auth/register";
    const response: Response | null = await this.postToApi<RegisterPost>(
      url,
      body,
    );
    if (!response) {
      return null;
    }
    return response.json();
  }
}
