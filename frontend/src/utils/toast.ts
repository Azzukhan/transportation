import { message } from "antd";

export const toast = {
  success: (content: string): void => {
    message.success(content);
  },
  error: (content: string): void => {
    message.error(content);
  },
  info: (content: string): void => {
    message.info(content);
  },
};
