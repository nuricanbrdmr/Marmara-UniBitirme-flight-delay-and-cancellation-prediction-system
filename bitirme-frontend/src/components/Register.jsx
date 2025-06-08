import { useState } from "react";
import { Form, Input, Button, Typography, Space, message } from "antd";
import {
  LockOutlined,
  CheckCircleOutlined,
  InfoCircleOutlined,
  MailOutlined,
} from "@ant-design/icons";
import { axiosPrivate } from "../api/axios";

const { Title, Text, Link } = Typography;

const KAYIT_URL = "/auth/register";

// Regex kuralları
export const SIFRE_REGEX =
  /^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%]).{8,24}$/;

// Tooltip mesajları için özel bileşen
export const SifreDogrulama = () => (
  <div>
    <p>• Şifre 8-24 karakter uzunluğunda olmalı</p>
    <p>• En az bir büyük ve küçük harf olmalı</p>
    <p>• En az bir rakam ve bir özel karakter (!@#$%) içermelidir</p>
  </div>
);

const Register = () => {
  const [form] = Form.useForm();
  const [yukleniyor, setYukleniyor] = useState(false);
  const [basarili, setBasarili] = useState(false);

  const onFinish = async (values) => {
    setYukleniyor(true);
    try {
      await axiosPrivate.post(KAYIT_URL, {
        email: values.email,
        password: values.password,
      });
      setBasarili(true);
      message.success("Kayıt başarılı!");
      form.resetFields();
    } catch (err) {
      message.error("Kayıt başarısız");
      setYukleniyor(false);
    }
  };

  // Şifre eşleşme kontrolü
  const SifreEslestirme = (_, value) => {
    if (!value) {
      return Promise.reject("Lütfen şifrenizi girin");
    }
    if (!SIFRE_REGEX.test(value)) {
      return Promise.reject(<SifreDogrulama />);
    }
    return Promise.resolve();
  };

  const EpostaKontrolu = (_, value) => {
    const emailRegExp = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!value || !emailRegExp.test(value)) {
      return Promise.reject("Geçerli bir e-posta adresi girin.");
    }
    return Promise.resolve();
  };

  if (basarili) {
    return (
      <div className="App">
        <Space
          direction="vertical"
          align="center"
          className="success-container"
        >
          <CheckCircleOutlined style={{ fontSize: 48, color: "#52c41a" }} />
          <Title level={2}>Kayıt Başarılı!</Title>
          <Link href="/login" strong>
            Giriş Yap
          </Link>
        </Space>
      </div>
    );
  }

  return (
    <div className="App">
      <Space
        direction="vertical"
        className="bg-white shadow-lg"
        style={{ width: "100%", maxWidth: 400, margin: "0 auto", padding: 24 }}
      >
        <Title level={2}>Kayıt Ol</Title>

        <Form
          form={form}
          name="register"
          onFinish={onFinish}
          layout="vertical"
          scrollToFirstError
        >
          <Form.Item
            name="email"
            label="Email"
            tooltip={{
              title: "Lütfen geçerli bir e-posta adresi girin.",
              icon: <InfoCircleOutlined />,
            }}
            rules={[{ validator: EpostaKontrolu }]}
          >
            <Input
              prefix={<MailOutlined />}
              placeholder="Uygun Email Adresi Girin.."
            />
          </Form.Item>

          <Form.Item
            name="password"
            label="Şifre"
            tooltip={{
              title: <SifreDogrulama />,
              icon: <InfoCircleOutlined />,
            }}
            rules={[{ validator: SifreEslestirme }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Uygun Şifre Girin.."
            />
          </Form.Item>

          <Form.Item
            name="confirm"
            label="Şifre Tekrar"
            dependencies={["password"]}
            rules={[
              { required: true, message: "Lütfen şifrenizi tekrar girin" },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue("password") === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject("Şifreler eşleşmiyor");
                },
              }),
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Şifre Doğrulama.."
            />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={yukleniyor} block>
              Kayıt Ol
            </Button>
          </Form.Item>

          <Text>
            Zaten hesabınız var mı? <Link href="/">Giriş Yap</Link>
          </Text>
        </Form>
      </Space>
    </div>
  );
};

export default Register;
