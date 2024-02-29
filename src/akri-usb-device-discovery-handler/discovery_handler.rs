use akri_discovery_utils::discovery::{
    v0::{discovery_handler_server::DiscoveryHandler, Device, DiscoverRequest, DiscoverResponse},
    DiscoverStream,
};
use anyhow::Result;
use async_trait::async_trait;
use std::collections::HashMap;
use std::env;
use std::process::Command;
use std::str;
use tokio_stream::wrappers::ReceiverStream;
use tonic::{Request, Response, Status};
use futures_util::StreamExt; // Corrected this

pub struct DiscoveryHandlerImpl {
    register_sender: tokio::sync::mpsc::Sender<()>,
    usb_camera_discovery_handler: UsbCameraDiscoveryHandler,
}

struct UsbCameraDiscoveryHandler {
    devices: HashMap<String, String>,
}

impl DiscoveryHandlerImpl {
    pub fn new(register_sender: tokio::sync::mpsc::Sender<()>) -> Self {
        DiscoveryHandlerImpl {
            register_sender,
            usb_camera_discovery_handler: UsbCameraDiscoveryHandler {
                devices: HashMap::new(),
            },
        }
    }
}

#[async_trait]
impl DiscoveryHandler for DiscoveryHandlerImpl {
    type DiscoverStream = DiscoverStream;
    async fn discover(
        &self,
        request: Request<DiscoverRequest>,
    ) -> Result<Response<Self::DiscoverStream>, Status> {
        let mut stream = self.usb_camera_discovery_handler.discover(request).await?.into_inner();

        let mut device_ids = Vec::new();
        while let Some(response) = stream.next().await {
            if let Ok(discover_response) = response {
                for device in discover_response.devices {
                    device_ids.push(device.id);
                }
            }
        }
        println!("Discovered device IDs: {:?}", device_ids);
        Ok(Response::new(stream))
    }
}

#[async_trait]
impl DiscoveryHandler for UsbCameraDiscoveryHandler {
    type DiscoverStream = ReceiverStream<Result<DiscoverResponse, Status>>;
    async fn discover(
        &self,
        _request: Request<DiscoverRequest>,
    ) -> Result<Response<Self::DiscoverStream>, Status> {
        println!("Starting discovery process...");
        let server_ip = env::var("SERVER_IP").map_err(|_| Status::unknown("SERVER_IP is not set"))?;
        println!("Server IP: {}", server_ip);
        let output = Command::new("usbip")
            .arg("list")
            .arg("-r")
            .arg(&server_ip)
            .output()
            .map_err(|_| Status::unknown("Failed to execute usbip command"))?;
        let output_str = str::from_utf8(&output.stdout).map_err(|_| Status::unknown("Could not convert output to string"))?;
        println!("usbip output: {}", output_str);
        let device_ids: Vec<String> = output_str
            .lines()
            .filter(|line| line.trim().starts_with(|c: char| c.is_digit(10)) && line.contains("-") && line.contains("."))
            .map(|line| line.split(':').next().unwrap().trim().to_string())
            .collect();
        println!("Device IDs: {:?}", device_ids);
        if !device_ids.is_empty() {
            let output = Command::new("sh")
                .arg("-c")
                .arg("modprobe vhci-hcd && echo 'vhci-hcd' >> /etc/modules")
                .output()
                .expect("Failed to execute command");
        
            println!("Output: {:?}", output);        
            for device_id in &device_ids {
                Command::new("usbip")
                    .arg("attach")
                    .arg("-r")
                    .arg(&server_ip)
                    .arg("-b")
                    .arg(device_id)
                    .output()
                    .map_err(|_| Status::unknown("Failed to attach device"))?;
                println!("Attached device: {}", device_id);
            }
        }

        let (mut tx, rx) = tokio::sync::mpsc::channel(4);
        for device_id in device_ids {
            let device = Device {
                id: device_id.clone(),
                properties: HashMap::new(),
                device_specs: vec![],
                mounts: vec![],
            };
            let response = DiscoverResponse { devices: vec![device] };
            tx.send(Ok(response)).await.unwrap();
            println!("Sent device: {}", device_id);
        }

        let stream = ReceiverStream::new(rx);
        println!("Finished discovery process");
        Ok(Response::new(stream))
    }
}