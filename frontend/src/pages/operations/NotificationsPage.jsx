import { useEffect, useState } from "react";
import { operationsApi } from "../../api/operations";
import { SectionHeader } from "../../components/shared/SectionHeader";
import { DataTable } from "../../components/shared/DataTable";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Textarea } from "../../components/ui/Textarea";
import { Select } from "../../components/ui/Select";
import { Button } from "../../components/ui/Button";

export function NotificationsPage() {
  const [notifications, setNotifications] = useState([]);
  const [form, setForm] = useState({ recipient: "", channel: "In-App", subject: "", message: "" });

  useEffect(() => {
    operationsApi.notifications().then((res) => setNotifications(res.data));
  }, []);

  const createNotification = async () => {
    await operationsApi.createNotification(form);
    setForm({ recipient: "", channel: "In-App", subject: "", message: "" });
    const { data } = await operationsApi.notifications();
    setNotifications(data);
  };

  const columns = [
    { key: "notification_id", label: "ID" },
    { key: "recipient", label: "Recipient" },
    { key: "channel", label: "Channel" },
    { key: "subject", label: "Subject" },
    { key: "status", label: "Status" },
  ];

  return (
    <div className="space-y-6">
      <SectionHeader title="Notification Center" subtitle="Track in-app and external notifications." />
      <Card>
        <div className="grid gap-4 md:grid-cols-2">
          <Input placeholder="Recipient" value={form.recipient} onChange={(e) => setForm({ ...form, recipient: e.target.value })} />
          <Select value={form.channel} onChange={(e) => setForm({ ...form, channel: e.target.value })}>
            <option>In-App</option>
            <option>Email</option>
            <option>SMS</option>
            <option>WhatsApp</option>
          </Select>
          <Input placeholder="Subject" value={form.subject} onChange={(e) => setForm({ ...form, subject: e.target.value })} />
          <Textarea placeholder="Message" rows="2" value={form.message} onChange={(e) => setForm({ ...form, message: e.target.value })} />
          <div className="md:col-span-2">
            <Button type="button" onClick={createNotification}>Create Notification</Button>
          </div>
        </div>
      </Card>
      <DataTable columns={columns} rows={notifications} emptyText="No notifications found." />
    </div>
  );
}
