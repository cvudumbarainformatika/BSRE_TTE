import Echo from 'laravel-echo'
import Pusher from 'pusher-js'

const host = 'xenter.my.id'

window.Pusher = Pusher

let echoInstance = null

export function getEchoInstance() {
  if (!echoInstance && typeof window !== 'undefined') {
    echoInstance = new Echo({
      broadcaster: 'pusher',
      key: 'simrs_key_harry141312',
      cluster: 'mt1',
      wsHost: host,
      encrypted: true,
      wssPort: 6002,
      wsPort: 6002,
      disableStats: true,
      forceTLS: true,
      enabledTransports: ['ws', 'wss']
    })
  }
  return echoInstance
}
