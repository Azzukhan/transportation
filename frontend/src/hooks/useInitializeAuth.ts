import { useEffect, useState } from "react";

import { useAppDispatch, useAppSelector } from "../app/hooks";
import {
  onLogout,
  onSetUser,
  onTokenRefresh,
  selectAccessToken,
  selectRefreshToken,
} from "../features/auth/authSlice";
import { getUser, logoutUser, refreshToken } from "../api/authentication";

let bootstrapPromise: Promise<void> | null = null;

export const useInitializeAuth = () => {
  const dispatch = useAppDispatch();
  const accessToken = useAppSelector(selectAccessToken);
  const refreshTokenValue = useAppSelector(selectRefreshToken);
  const [isInitializingAuth, setIsInitializingAuth] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const initialize = async () => {
      if (!refreshTokenValue) {
        if (accessToken) {
          try {
            const user = await getUser();
            dispatch(onSetUser(user));
          } catch {
            dispatch(onLogout());
          }
        } else {
          dispatch(onLogout());
        }

        if (isMounted) {
          setIsInitializingAuth(false);
        }
        return;
      }

      if (!bootstrapPromise) {
        bootstrapPromise = (async () => {
          try {
            const refreshed = await refreshToken(refreshTokenValue);
            dispatch(
              onTokenRefresh({
                accessToken: refreshed.accessToken,
                refreshToken: refreshed.refreshToken,
              }),
            );

            const user = await getUser();
            dispatch(onSetUser(user));
          } catch {
            try {
              await logoutUser();
            } catch {
              // Ignore logout endpoint failures for compatibility with current backend.
            }
            dispatch(onSetUser(null));
            dispatch(onLogout());
          }
        })();
      }

      try {
        await bootstrapPromise;
      } finally {
        if (isMounted) {
          setIsInitializingAuth(false);
        }
      }
    };

    void initialize();

    return () => {
      isMounted = false;
    };
  }, [accessToken, dispatch, refreshTokenValue]);

  return { isInitializingAuth };
};
