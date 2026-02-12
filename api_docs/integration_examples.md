# Integration Examples

## Complete Practice Management Integration

### Python Integration

```python
import asyncio
from datetime import datetime, timedelta
from hardcard_api import HardCardClient

class VeterinaryPracticeManager:
    def __init__(self, api_token):
        self.client = HardCardClient(token=api_token)
    
    async def daily_operations(self):
        """Run daily practice operations"""
        
        # 1. Check system health
        health = await self.client.health.check()
        if health.status != "healthy":
            await self.notify_admin("System health issue detected")
        
        # 2. Process morning appointment reminders
        tomorrow = datetime.now() + timedelta(days=1)
        appointments = await self.client.appointments.list(
            date=tomorrow.date(),
            status="scheduled"
        )
        
        for appointment in appointments:
            await self.client.phone_agent.call(
                phone_number=appointment.client.phone,
                call_type="reminder",
                context={
                    "appointment_time": appointment.datetime.isoformat(),
                    "patient_name": appointment.patient.name,
                    "service_type": appointment.service_type
                }
            )
        
        # 3. Generate daily analytics report
        analytics = await self.client.analytics.daily_summary()
        await self.send_daily_report(analytics)
    
    async def handle_emergency_call(self, phone_number):
        """Handle incoming emergency call"""
        
        # Initiate emergency triage call
        call = await self.client.phone_agent.call(
            phone_number=phone_number,
            call_type="emergency",
            priority="high",
            context={
                "clinic_hours": "8AM-6PM",
                "emergency_contact": "+1-800-VET-HELP"
            }
        )
        
        # Monitor call in real-time
        async for update in self.client.phone_agent.stream(call.call_id):
            if update.status == "emergency_detected":
                await self.alert_veterinarian(update.details)
            elif update.status == "completed":
                await self.log_emergency_call(update.summary)

# Usage
manager = VeterinaryPracticeManager("your_api_token")
asyncio.run(manager.daily_operations())
```

### JavaScript/Node.js Integration

```javascript
const { HardCardAPI } = require('@hardcard/api');

class PracticeWebsite {
    constructor(apiToken) {
        this.api = new HardCardAPI({ token: apiToken });
    }
    
    // Online appointment booking form
    async bookAppointment(formData) {
        try {
            // Create client if new
            let client;
            try {
                client = await this.api.clients.findByEmail(formData.email);
            } catch (error) {
                client = await this.api.clients.create({
                    name: formData.name,
                    email: formData.email,
                    phone: formData.phone
                });
            }
            
            // Create patient if new
            let patient = await this.api.patients.findByName(
                formData.petName, 
                client.id
            );
            if (!patient) {
                patient = await this.api.patients.create({
                    name: formData.petName,
                    species: formData.species,
                    breed: formData.breed,
                    client_id: client.id
                });
            }
            
            // Check availability
            const availability = await this.api.appointments.checkAvailability({
                date: formData.preferredDate,
                service_type: formData.serviceType
            });
            
            if (availability.slots.length === 0) {
                // Use AI agent to find alternative times
                const call = await this.api.phoneAgent.call({
                    phone_number: client.phone,
                    call_type: "appointment",
                    context: {
                        requested_date: formData.preferredDate,
                        service_type: formData.serviceType,
                        flexibility: "high"
                    }
                });
                
                return { 
                    status: "scheduled_via_phone",
                    call_id: call.call_id,
                    message: "We'll call you to find the best available time"
                };
            }
            
            // Book appointment
            const appointment = await this.api.appointments.create({
                client_id: client.id,
                patient_id: patient.id,
                datetime: availability.slots[0].datetime,
                service_type: formData.serviceType,
                notes: formData.notes
            });
            
            // Send confirmation
            await this.api.phoneAgent.call({
                phone_number: client.phone,
                call_type: "confirmation",
                context: {
                    appointment_id: appointment.id,
                    datetime: appointment.datetime
                }
            });
            
            return { 
                status: "confirmed",
                appointment_id: appointment.id 
            };
            
        } catch (error) {
            console.error('Booking error:', error);
            throw new Error('Failed to book appointment');
        }
    }
    
    // Real-time chat widget integration
    setupChatWidget() {
        const widget = document.getElementById('chat-widget');
        
        widget.addEventListener('message', async (event) => {
            const message = event.detail.message;
            
            // Use MUSE for intelligent response generation
            const response = await this.api.muse.generateResponse({
                message: message,
                context: "veterinary_support",
                personality: "helpful_professional"
            });
            
            widget.addMessage({
                text: response.text,
                type: 'bot',
                timestamp: new Date()
            });
            
            // Escalate to phone call if needed
            if (response.escalation_recommended) {
                const callButton = widget.addCallButton();
                callButton.onclick = () => this.initiateSupportCall();
            }
        });
    }
    
    async initiateSupport() {
        const call = await this.api.phoneAgent.call({
            phone_number: this.currentUser.phone,
            call_type: "support",
            context: {
                user_id: this.currentUser.id,
                page_url: window.location.href,
                previous_interactions: this.getRecentInteractions()
            }
        });
        
        // Show call status in UI
        this.showCallStatus(call.call_id);
    }
}
```

### React Component Integration

```jsx
import React, { useState, useEffect } from 'react';
import { useHardCardAPI } from '@hardcard/react-hooks';

const AppointmentBooking = () => {
    const { api, loading } = useHardCardAPI();
    const [formData, setFormData] = useState({});
    const [availability, setAvailability] = useState([]);
    const [bookingStatus, setBookingStatus] = useState('idle');
    
    // Real-time availability checking
    useEffect(() => {
        if (formData.date && formData.serviceType) {
            checkAvailability();
        }
    }, [formData.date, formData.serviceType]);
    
    const checkAvailability = async () => {
        const slots = await api.appointments.checkAvailability({
            date: formData.date,
            service_type: formData.serviceType
        });
        setAvailability(slots);
    };
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        setBookingStatus('booking');
        
        try {
            if (availability.length === 0) {
                // No slots available - use AI phone agent
                const call = await api.phoneAgent.call({
                    phone_number: formData.phone,
                    call_type: "appointment",
                    context: {
                        preferred_date: formData.date,
                        service_type: formData.serviceType,
                        pet_name: formData.petName,
                        owner_name: formData.name
                    }
                });
                
                setBookingStatus('scheduled_for_callback');
                // Monitor call status
                monitorCall(call.call_id);
                
            } else {
                // Direct booking available
                const appointment = await api.appointments.create({
                    datetime: formData.selectedSlot,
                    client: formData,
                    service_type: formData.serviceType
                });
                
                setBookingStatus('confirmed');
            }
        } catch (error) {
            setBookingStatus('error');
            console.error('Booking failed:', error);
        }
    };
    
    const monitorCall = (callId) => {
        const ws = new WebSocket(`wss://api.hardcard.com/ws/call/${callId}`);
        
        ws.onmessage = (event) => {
            const update = JSON.parse(event.data);
            
            if (update.status === 'completed' && update.outcome === 'appointment_booked') {
                setBookingStatus('confirmed');
            }
        };
    };
    
    return (
        <form onSubmit={handleSubmit}>
            {/* Form fields */}
            
            {availability.length === 0 && formData.date && (
                <div className="no-availability">
                    <p>No slots available for your preferred time.</p>
                    <p>We'll call you to find the best alternative!</p>
                </div>
            )}
            
            {bookingStatus === 'scheduled_for_callback' && (
                <CallStatusMonitor 
                    message="We're calling you now to schedule your appointment!"
                />
            )}
            
            <button type="submit" disabled={loading || bookingStatus === 'booking'}>
                {bookingStatus === 'booking' ? 'Booking...' : 'Book Appointment'}
            </button>
        </form>
    );
};
```

## MUSE Creative Integration

```python
# Advanced MUSE integration for creative veterinary content
class CreativeVetContent:
    def __init__(self, api_client):
        self.api = api_client
    
    async def generate_educational_content(self, topic):
        """Generate educational content using MUSE creativity"""
        
        # Use sacred geometry poetry for engaging content
        poetry = await self.api.muse.poetry.generate({
            "theme": topic,
            "style": "educational",
            "mathematical_elements": ["fibonacci", "phi", "fractals"],
            "target_audience": "pet_owners"
        })
        
        # Generate accompanying music for content
        music = await self.api.muse.music.compose({
            "mood": "calming",
            "tempo": 60,  # Slow tempo for learning
            "instrumentation": ["piano", "strings"],
            "duration": 180  # 3 minutes
        })
        
        # Create video visualization
        video = await self.api.muse.video.generate({
            "script": poetry.verses,
            "background_music": music.audio_url,
            "visual_style": "sacred_geometry",
            "animations": ["golden_spiral", "flower_of_life"]
        })
        
        return {
            "content": poetry,
            "audio": music,
            "video": video,
            "engagement_score": await self.predict_engagement(poetry, music)
        }
    
    async def create_appointment_reminder_song(self, appointment):
        """Create personalized reminder song for appointment"""
        
        song = await self.api.muse.music.personalized_composition({
            "pet_name": appointment.patient.name,
            "appointment_type": appointment.service_type,
            "client_preferences": appointment.client.music_preferences,
            "mathematical_harmony": "phi_based",
            "frequency_healing": "528hz"  # Love frequency
        })
        
        return song
```

## Complete Error Handling

```python
from hardcard_api.exceptions import (
    HardCardAPIError, 
    AuthenticationError, 
    RateLimitError,
    ValidationError
)

class RobustVetPlatform:
    def __init__(self, api_token):
        self.api = HardCardClient(token=api_token)
        self.retry_count = 3
        self.backoff_factor = 2
    
    async def robust_api_call(self, api_method, *args, **kwargs):
        """Robust API call with retry logic and error handling"""
        
        for attempt in range(self.retry_count):
            try:
                return await api_method(*args, **kwargs)
                
            except AuthenticationError:
                # Token expired - refresh and retry
                await self.refresh_token()
                if attempt == self.retry_count - 1:
                    raise
                    
            except RateLimitError as e:
                # Rate limited - wait and retry
                wait_time = e.retry_after or (self.backoff_factor ** attempt)
                await asyncio.sleep(wait_time)
                if attempt == self.retry_count - 1:
                    raise
                    
            except ValidationError as e:
                # Validation error - fix data and retry once
                if attempt == 0:
                    kwargs = self.fix_validation_errors(kwargs, e.errors)
                else:
                    raise
                    
            except HardCardAPIError as e:
                # Server error - retry with backoff
                if e.status_code >= 500 and attempt < self.retry_count - 1:
                    await asyncio.sleep(self.backoff_factor ** attempt)
                else:
                    raise
    
    async def graceful_degradation_call(self, phone_number, context):
        """Phone call with graceful degradation"""
        
        try:
            # Try AI phone agent first
            return await self.robust_api_call(
                self.api.phone_agent.call,
                phone_number=phone_number,
                call_type="appointment",
                context=context
            )
        except Exception:
            # Fall back to SMS notification
            return await self.send_sms_fallback(phone_number, context)
    
    async def send_sms_fallback(self, phone_number, context):
        """SMS fallback when phone agent unavailable"""
        
        message = f"Hi! This is {context.get('clinic_name', 'your vet clinic')}. "
        message += f"Please call us at {context.get('clinic_phone')} to schedule "
        message += f"an appointment for {context.get('pet_name', 'your pet')}."
        
        return await self.api.sms.send({
            "to": phone_number,
            "message": message,
            "fallback_method": "email"
        })
```

This comprehensive integration guide shows how to build robust, production-ready applications using the HardCard API with proper error handling, real-time features, and creative MUSE integration.
