import type { Mountain, Trail } from '../types';

interface GpxWaypoint {
  name: string;
  lat: number;
  lon: number;
  ele?: number;
  description?: string;
}

export function generateMountainGpx(mountain: Mountain): string {
  if (!mountain.latitude || !mountain.longitude) {
    throw new Error('산 좌표 정보가 없습니다');
  }

  const waypoints: GpxWaypoint[] = [
    {
      name: mountain.certification_point || mountain.name,
      lat: mountain.latitude,
      lon: mountain.longitude,
      ele: mountain.altitude || undefined,
      description: `블랙야크 100대 명산 인증지 - ${mountain.name}`,
    },
  ];

  return generateGpxXml({
    name: `${mountain.name} 인증지`,
    description: `블랙야크 100대 명산 - ${mountain.name} (${mountain.region})`,
    waypoints,
  });
}

export function generateTrailGpx(mountain: Mountain, trail: Trail): string {
  const waypoints: GpxWaypoint[] = [];

  // 들머리
  if (trail.trail_head && mountain.latitude && mountain.longitude) {
    waypoints.push({
      name: `들머리: ${trail.trail_head}`,
      lat: mountain.latitude,
      lon: mountain.longitude,
    });
  }

  // 인증지 (정상)
  if (mountain.latitude && mountain.longitude) {
    waypoints.push({
      name: mountain.certification_point || '정상',
      lat: mountain.latitude,
      lon: mountain.longitude,
      ele: mountain.altitude || undefined,
    });
  }

  return generateGpxXml({
    name: `${mountain.name} - ${trail.name}`,
    description: trail.description || `${mountain.name} ${trail.name} 코스`,
    waypoints,
  });
}

interface GpxOptions {
  name: string;
  description?: string;
  waypoints: GpxWaypoint[];
}

function generateGpxXml(options: GpxOptions): string {
  const { name, description, waypoints } = options;
  const timestamp = new Date().toISOString();

  const waypointXml = waypoints
    .map(
      (wp) => `
  <wpt lat="${wp.lat}" lon="${wp.lon}">
    <name>${escapeXml(wp.name)}</name>${wp.ele ? `
    <ele>${wp.ele}</ele>` : ''}${wp.description ? `
    <desc>${escapeXml(wp.description)}</desc>` : ''}
    <sym>Summit</sym>
  </wpt>`
    )
    .join('');

  return `<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="BlackYak 100 Mountain Tracker"
  xmlns="http://www.topografix.com/GPX/1/1"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
  <metadata>
    <name>${escapeXml(name)}</name>${description ? `
    <desc>${escapeXml(description)}</desc>` : ''}
    <author>
      <name>BlackYak 100 Mountain Tracker</name>
    </author>
    <time>${timestamp}</time>
  </metadata>${waypointXml}
</gpx>`;
}

function escapeXml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

export function downloadGpx(filename: string, gpxContent: string): void {
  const blob = new Blob([gpxContent], { type: 'application/gpx+xml' });
  const url = URL.createObjectURL(blob);

  const link = document.createElement('a');
  link.href = url;
  link.download = filename.endsWith('.gpx') ? filename : `${filename}.gpx`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  URL.revokeObjectURL(url);
}
