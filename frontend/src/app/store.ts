import { configureStore } from "@reduxjs/toolkit";

import { authReducer } from "../features/auth/authSlice";
import { gridReducer } from "../features/grid/gridSlice";

export const store = configureStore({
  reducer: {
    auth: authReducer,
    grid: gridReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
