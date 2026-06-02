# Student Buddy Frontend

This is a Next.js and Material UI (MUI) frontend web application for Student Buddy. It allows students to undergo an onboarding questionnaire to establish their academic and well-being profile, and then talk to their advisor agent via a chat interface.

---

## 📁 Directory Structure & Key Files

- [src/app/page.tsx](file:///home/snipeart007/repos/student-buddy/frontend/src/app/page.tsx): Main entrypoint which conditionally mounts either the Onboarding stepper or the Chat interface depending on the state of the user.
- [src/components/Onboarding.tsx](file:///home/snipeart007/repos/student-buddy/frontend/src/components/Onboarding.tsx): A multi-step form stepper (built using MUI components) that gathers the student's background, grades, subjects, strengths, goals, learning style, and stress levels.
- [src/components/Chat.tsx](file:///home/snipeart007/repos/student-buddy/frontend/src/components/Chat.tsx): Embeds the advisor chat interface.
- [src/components/Navbar.tsx](file:///home/snipeart007/repos/student-buddy/frontend/src/components/Navbar.tsx): Common application navigation bar.
- [src/components/ThemeRegistry.tsx](file:///home/snipeart007/repos/student-buddy/frontend/src/components/ThemeRegistry.tsx): Configures MUI theme registries and settings.
- [src/lib/api.ts](file:///home/snipeart007/repos/student-buddy/frontend/src/lib/api.ts): Encapsulates API requests to the local backend endpoints `/auth/register`, `/auth/login`, and `/onboarding`.

---

## ⚠️ Current Implementation Status: Incomplete

> [!WARNING]
> ### Chat UI Incompletion
> Currently, the [Chat.tsx](file:///home/snipeart007/repos/student-buddy/frontend/src/components/Chat.tsx) component is implemented using a simple HTML `<iframe>` that displays the mounted Gradio UI directly:
> 
> ```tsx
> <iframe
>   src="/advisor_chat/"
>   style={{ width: '100%', height: '100%', border: 'none' }}
>   title="Gradio Chat Interface"
> />
> ```
> 
> **Original Requirement Specifications**:
> 1. The backend must serve a **headless** Gradio Blocks API (no UI, API only).
> 2. The frontend must implement the Chat interface using custom **MUI special chat components**.
> 3. The frontend must manage communication and streaming with the backend using the `@gradio/client` library.
> 
> In the current version, the `@gradio/client` package is not yet integrated on the frontend, and the raw Gradio interface is displayed instead of native MUI chat bubbles and formatting.

---

## 🚀 Running the Frontend

### Development Mode
To run the Next.js development server locally (usually at `http://localhost:3000`):

```bash
npm install
npm run dev
```

### Building for Production / Local Hosting
The backend is designed to serve the built static assets of the frontend. To build and compile the application for static export:

```bash
npm run build
```
This command compiles the React code and exports it as static HTML/JS/CSS files in the `out/` folder, which the FastAPI server then mounts at root (`/`) for deployment.
