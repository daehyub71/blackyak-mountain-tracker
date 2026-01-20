import { Link } from 'react-router-dom';
import type { Mountain } from '../../types';

interface MountainCardProps {
  mountain: Mountain;
}

export function MountainCard({ mountain }: MountainCardProps) {
  return (
    <Link
      to={`/mountain/${mountain.id}`}
      className="group block"
    >
      {/* Image Container */}
      <div className="aspect-square bg-gray-50 rounded-2xl overflow-hidden mb-3 border border-gray-100">
        {mountain.image_url ? (
          <img
            src={mountain.image_url}
            alt={mountain.name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-emerald-50 to-teal-50">
            <span className="text-5xl opacity-60">⛰️</span>
          </div>
        )}
      </div>

      {/* Info */}
      <div className="px-1">
        <h3 className="font-semibold text-gray-900 group-hover:text-primary transition-colors truncate">
          {mountain.name}
        </h3>
        <p className="mt-0.5 text-sm text-gray-500 truncate">
          {mountain.region}
          {mountain.altitude && (
            <span className="text-gray-400"> · {mountain.altitude.toLocaleString()}m</span>
          )}
        </p>
      </div>
    </Link>
  );
}
