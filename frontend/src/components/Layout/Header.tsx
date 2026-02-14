import { LogoutOutlined } from "@ant-design/icons";
import { Button, Space, Tag, Typography } from "antd";

import { useAppDispatch, useAppSelector } from "../../app/hooks";
import { logoutUser } from "../../api/authentication";
import { LogoLockup } from "../Brand/LogoLockup";
import { onLogout, selectUser } from "../../features/auth/authSlice";

const { Text } = Typography;

export const Header = () => {
  const dispatch = useAppDispatch();
  const user = useAppSelector(selectUser);

  const handleLogout = async (): Promise<void> => {
    try {
      await logoutUser();
    } catch {
      // ignore API compatibility issues
    }
    dispatch(onLogout());
  };

  return (
    <header className="admin-header">
      <div className="admin-header-title">
        <LogoLockup size="sm" subtitle="Operations Workspace" />
        <Tag color="blue">Premium Panel</Tag>
      </div>

      <Space>
        <Text type="secondary" className="admin-user-pill">
          {user?.username ?? "Guest"}
        </Text>
        <Button icon={<LogoutOutlined />} onClick={() => void handleLogout()}>
          Logout
        </Button>
      </Space>
    </header>
  );
};
