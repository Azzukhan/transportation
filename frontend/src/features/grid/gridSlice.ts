import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

export type GridState = {
  page: number;
  pageSize: number;
};

const initialState: GridState = {
  page: 1,
  pageSize: 10,
};

const gridSlice = createSlice({
  name: "grid",
  initialState,
  reducers: {
    setPage: (state, action: PayloadAction<number>) => {
      state.page = action.payload;
    },
    setPageSize: (state, action: PayloadAction<number>) => {
      state.pageSize = action.payload;
    },
    resetGridState: () => initialState,
  },
});

export const { setPage, setPageSize, resetGridState } = gridSlice.actions;
export const gridReducer = gridSlice.reducer;
