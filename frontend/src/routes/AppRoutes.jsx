import React from "react";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import AppLayout from "@/layout/AppLayout.jsx";
import HomePage from "@/pages/HomePage.jsx";
import AnalyzePage from "@/pages/AnalyzePage.jsx";
import MemoryPage from "@/pages/MemoryPage.jsx";
import AboutPage from "@/pages/AboutPage.jsx";

const AppRoutes = () => {
  const router = createBrowserRouter([
    {
      path: "/",
      element: <AppLayout />,
      children: [
        { index: true,      element: <HomePage />    },
        { path: "analyze",  element: <AnalyzePage /> },
        { path: "memory",   element: <MemoryPage />  },
        { path: "about",    element: <AboutPage />   },
      ],
    },
  ]);

  return <RouterProvider router={router} />;
};

export default AppRoutes;
